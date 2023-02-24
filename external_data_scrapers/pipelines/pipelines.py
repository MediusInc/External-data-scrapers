from opensearchpy import OpenSearch, exceptions

class OpenSearchPipeline:

    def __init__(self, index_name):
        self.index_name = "external_data_scrapers_" + index_name

        self.client = OpenSearch(
            hosts = [{"host": "localhost", "port": 9292}],
            use_ssl = False,
            verify_certs = False,
            ssl_assert_hostname = False,
            ssl_show_warn = False
        )

        try:
            self.client.indices.create(self.index_name, body=self.mapping)
            print("A new index {index_name} was created.")
        except exceptions.RequestError:
            # Test if there exists an index and calculate the index_name that will be used
            if(not self._get_first_compatible_index()):
                # Create the index with the new mapping                
                self.client.indices.create(self.index_name, body=self.mapping)
            else:
                print("The index {self.index_name} was not created as it already exists.")

    def _get_first_compatible_index(self) -> bool:
        """The functions iterates over the index names that are possible based on the initial
        index_name and returns True if it finds an index whose mapping matches the self.mapping.
        If such index does not exists False is returned. After executing this methode the
        self.index_name contains the name of the index that will be used.

        :return: Boolean indicating if there exists an index that has a matching mapping.
        :rtype: bool
        """

        # Iterate over indices that exists
        while(self.client.indices.exists(self.index_name)):
            # Test if mapping is the same (if it is return true - no new index needs to be created)
            if(self.client.indices.get_mapping( self.index_name )[self.index_name]["mappings"] == self.mapping["mappings"]):
                return True

            # Construct self.index name with the next index that needs to be checked
            try:
                # This handles cases when the self.index_name already has _ddd at the end
                index_id = int(self.index_name[-3:]) + 1
                self.index_name = self.index_name[:-3] + format(index_id, '03d')
            except ValueError:
                # This handles cases in which the index_name does not end with _ddd
                index_id = 1
                self.index_name += "_"
                self.index_name += format(index_id, '03d')
        
        # If no index exsists that has the same mapping return False
        return False

    def process_item(self, item, spider):
        pass 

    def close_spider(self, spider):
        pass

class ParkingAvailabilityPipeline(OpenSearchPipeline):
    def __init__(self):
        self.mapping = {
            "settings" : {
                "index": {
                    "number_of_shards" : 1,
                    "number_of_replicas" : 0
                }
            },
            "mappings":{
                "properties": {
                    "timestamp": {"type": "date", "format": "epoch_millis"},
                    "location": {"type": "text", "analyzer": "standard"},
                    "daily_available": {"type": "integer"},
                    "daily_free": {"type": "integer"},
                    "subscriber_available": {"type": "integer"},
                    "subscriber_rented": {"type": "integer"},
                    "subscriber_free": {"type": "integer"},
                    "subscriber_waiting_list": {"type": "integer"}
                }
            }
        }
        index_name = "parking_availability"
        super().__init__(index_name)
    
    def process_item(self, item, spider):
        body = {
            "timestamp": item["date"],
            "location": item["location"],
            "daily_available": item["daily_available"],
            "daily_free": item["daily_free"],
            "subscriber_available": item["subscriber_available"],
            "subscriber_rented": item["subscriber_rented"],
            "subscriber_free": item["subscriber_free"],
            "subscriber_waiting_list": item["subscriber_waiting_list"]
        }    
        self.client.index(index=self.index_name, body=body)

        return item   
