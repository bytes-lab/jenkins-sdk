## Jenkins API

#### All requests are POST

- sign up and get token

	``` 
    /api/v1/get_token/	
	{
	  "url":"http://127.0.0.1:8080",
	  "username": "demo",
	  "password": "demo"
	}
    ```

- create a job
	```
	/api/v1/create_job/
	header: token:<token>
	{	
    	"name":"empty-2", 
        "config_xml":"<xml></xml>"
    }
    ```

- delete a job
	```
	/api/v1/delete_job/
	header: token:<token>
	{
    	"name":"empty"
    }
    ```

- copy a job
 	```
	/api/v1/copy_job/
	header: token:<token>
	{
    	"from_name":"empty-1", 
        "to_name":"empty-3"
    }
    ```

- reconfigure a job
	```
	/api/v1/reconfig_job/
	header: token:<token>
	{
    	"name":"empty-1",
    	"config_xml":"<xml></xml>"
    }
    ```

- get status of a job
	```
	/api/v1/status_job/
	header: token:<token>
	{
    	"name":"first_job", 
        "depth": 1, 
        "fetch_all_builds":true
    }
    ```

- start build a job
	```
	/api/v1/start_build/
	header: token:<token>
	{
    	"name":"empty-1", 
        "params1":{
        	"first":1, 
            "second":2
        }
    }
    ```

- stop build a job
	```
	/api/v1/stop_build/
	header: token:<token>
	{
    	"name":"empty-1", 
        "build_number":3
    }
    ```

- create a node
	```
	/api/v1/create_node/
	header: token:<token>
	{
		"name":"node-3",
		"numExecutors":5,
		"nodeDescription":"nodeDescription",
		"labels":"labels",
		"exclusive":true
	}
    ```

- delete a node
	```
	/api/v1/delete_node/
	header: token:<token>
	{
    	"name":"node-1"
    }
    ```

- disable a node
	```
	/api/v1/disable_node/
	header: token:<token>
	{
    	"name":"node-2"
    }
    ```

- install plugin
	```
	/api/v1/install_plugin/
	header: token:<token>
	{
    	"name":"CCM Plug-in", 
        "include_dependencies":false 
    }
    ```
