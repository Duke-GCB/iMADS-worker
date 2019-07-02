import yaml


class ConfigLoader:
    """
    Extracts a configuration dictionary information from a YAML document storing metadata about prediction tracks
    """
    model_id_key = 'track_name'

    # Given a model identifier such as E2F4_0002(JS) and a YAML document with metadata
    def __init__(self, model_id, metadata_file_name):
        """
        Creates a loader ready to extract a single config object
        Parameters
        ----------
        model_id: string identifier of the track name to load (e.g. E2F4_0002(JS))
        metadata_file_name: Path to the yaml metadata file containing all track metadata (e.g. tracks.yaml)
        """
        if model_id is None:
            raise ValueError('model_id is required')
        if metadata_file_name is None:
            raise ValueError('metadata_file_name is required')
        self.model_id = model_id
        self.metadata_file_name = metadata_file_name
        self._config = None

    def find_config(self):
        """
        Loads the configuration from the YAML file, and returns the first entry matching self.model_id
        Returns
        -------
        A config dictionary. Note that the tracks.yaml file will likely have two entries matching a model_id:
        an hg19 version and an hg38 version. Both are identical (except for the assembly) parameter, so
        we only return the first
        """
        with open(self.metadata_file_name, 'r') as metadata_file:
            configs = yaml.safe_load(metadata_file)
            matching_configs = [c for c in configs if c[ConfigLoader.model_id_key] == self.model_id]
            if matching_configs:
                return matching_configs[0]
        return None

    @property
    def config(self):
        """
        Lazy property reader for config
        Returns
        -------
        The config returned by find_config, or None if none matched

        """
        if self._config is None:
            self._config = self.find_config()
        return self._config
