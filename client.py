#!/usr/bin/env python3

from __future__ import print_function
import requests
from requests.auth import HTTPBasicAuth
import base64
from multiprocessing import Pool, TimeoutError
from worker import PredictionsWorker
import time
import tempfile
import os
import traceback
from config import Config


class Status(object):
    """
    Status constants for API
    """
    new = 'NEW'
    running = 'RUNNING'
    complete = 'COMPLETE'
    error = 'ERROR'


class PredictionsClient(object):
    claim_interval = 0.5

    def __init__(self, config):
        """
        Initialize a client for running prediction jobs

        """
        self.config = config

    def make_url(self, part):
        return "{}/{}".format(self.config.base_url, part)

    def _make_auth(self):
        return HTTPBasicAuth(self.config.worker_username, self.config.worker_password)

    def get_new_jobs(self):
        url = self.make_url("jobs?job_status={}".format(Status.new))
        r = requests.get(url, auth=self._make_auth())
        r.raise_for_status()
        return r.json()['result']

    def get_first_new_job(self):
        new_jobs = self.get_new_jobs()
        if new_jobs:
            return new_jobs[0]
        else:
            return None

    def claim_job(self, job):
        self._update_job_status(job, Status.running)

    def mark_job_complete(self, job):
        self._update_job_status(job, Status.complete)

    def mark_job_error(self, job, message):
        self._update_job_status(job, Status.error, error_message=message)

    def _update_job_status(self, job, status, error_message=None):
        url = self.make_url("jobs/{}".format(job['id']))
        data = {'job_status': status}
        if error_message:
            data['error_message'] = error_message
        r = requests.put(url, auth=self._make_auth(), json=data)
        r.raise_for_status()

    def get_sequence(self, job):
        url = self.make_url("sequences/{}".format(job['sequence_list']))
        r = requests.get(url, auth=self._make_auth())
        r.raise_for_status()
        data = r.json()['data']
        return base64.b64decode(data)

    def save_custom_predictions(self, job, bed_file_data):
        url = self.make_url("custom_predictions")
        r = requests.post(url, auth=self._make_auth(), json={
            'job_id': job['id'],
            'model_name': job['model_name'],
            'bed_data': bed_file_data,
        })
        r.raise_for_status()

    @staticmethod
    def write_data(data, filename):
        with open(filename, 'w') as f:
            f.write(data.decode('utf-8'))

    @staticmethod
    def read_data(filename):
        with open(filename, 'r') as f:
            return f.read().encode('utf-8')

    def make_predictions(self, job):
        # Write the fasta data to a local file
        fasta_data = self.get_sequence(job)
        _, sequence_file = tempfile.mkstemp(suffix='.fa', prefix='prediction', dir=self.config.output_dir)
        self.write_data(fasta_data, sequence_file)
        model_name = job['model_name']
        worker = PredictionsWorker(self.config)
        bed_file = worker.run(sequence_file, model_name)
        os.unlink(sequence_file)
        return self.read_data(bed_file)

    def list_jobs(self):
        print("NEW JOBS")
        for job in self.get_new_jobs():
            print('id:', job['id'])
            print('     model:', job['model_name'], ' type:', job['type'], 'sequence:', job['sequence_list'])
        print()

    def run_job(self, job):
        print('Starting predictions\n{}'.format(job))
        bed_file_data = self.make_predictions(job)
        print('Saving predictions for job with id {}:\n{}\n...'.format(job['id'], bed_file_data[:50]))
        self.save_custom_predictions(job, base64.b64encode(bed_file_data))
        print('Completing job with id {}'.format(job['id']))
        self.mark_job_complete(job)
        print('Completed job with id {}'.format(job['id']))

    def claim_loop(self):
        print('Starting predictions worker, polling every {}s'.format(self.claim_interval))
        pool = Pool()
        async_results = []
        while True:
            # Check for the the first job
            try:
                job = self.get_first_new_job()
                if job:
                    # Claim it
                    print('Claiming job\n{}'.format(job))
                    self.claim_job(job)
                    result = pool.apply_async(run_job, (self, job))
                    # Add the async_result and the job to the dictionary so that we can check on it later
                    async_results.append(dict(job=job, result=result))
            except:
                print('Exception checking for prediction jobs:\n', traceback.format_exc())
                time.sleep(10)

            # Sleep
            time.sleep(self.claim_interval)
            # Check on results and cleanup
            to_remove = list()
            for index, result_dict in enumerate(async_results):
                job, async_result = result_dict['job'], result_dict['result']
                try:
                    # Don't wait to see if the result is ready
                    result = async_result.get(timeout=0)
                    # If we reach this line, the job has been completed
                    to_remove.append(index)
                except TimeoutError:
                    # Result not ready, we'll try again later
                    pass
                except:
                    # There was some exception, log it and send it back
                    s = traceback.format_exc()
                    print('Exception making predictions:\n', s)
                    self.mark_job_error(job, str(s))
                    to_remove.append(index)
            # Now remove the completed or errored jobs
            async_results = [r for index, r in enumerate(async_results) if index not in to_remove]

# apply_async does not work on instance methods, so we declare a simple function
def run_job(cli, job):
    cli.run_job(job)

if __name__ == '__main__':
    c = Config()
    # Local overrides
    cli = PredictionsClient(c)
    cli.claim_loop()
