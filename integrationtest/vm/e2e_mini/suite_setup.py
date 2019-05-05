'''

@author: Frank
'''


import os.path
import zstacklib.utils.linux as linux
import zstacklib.utils.http as  http
import zstacklib.utils.ssh as ssh
import subprocess
import zstackwoodpecker.operations.scenario_operations as scenario_operations
import zstackwoodpecker.operations.deploy_operations as deploy_operations
import zstackwoodpecker.operations.config_operations as config_operations
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.tag_operations as tag_ops
import zstacktestagent.plugins.host as host_plugin
import zstacktestagent.testagent as testagent
import zstacklib.utils.xmlobject as xmlobject

CREATE_SNAPSHOT_PATH = "/ceph/primarystorage/snapshot/create"
CP_PATH = "/ceph/primarystorage/volume/cp"
UPLOAD_IMAGESTORE_PATH = "/ceph/primarystorage/imagestore/backupstorage/commit"
LOCAL_CREATE_TEMPLATE_FROM_VOLUME = "/localstorage/volume/createtemplate"
KVM_TAKE_VOLUME_SNAPSHOT_PATH = "/vm/volume/takesnapshot"
LOCAL_COMMIT_TO_IMAGESTORE_PATH = "/localstorage/imagestore/commit"
LOCAL_UPLOAD_TO_IMAGESTORE_PATH = "/localstorage/imagestore/upload"
NFS_CREATE_TEMPLATE_FROM_VOLUME_PATH = "/nfsprimarystorage/sftp/createtemplatefromvolume"
NFS_COMMIT_TO_IMAGESTORE_PATH = "/nfsprimarystorage/imagestore/commit"
NFS_UPLOAD_TO_IMAGESTORE_PATH = "/nfsprimarystorage/imagestore/upload"
SMP_CREATE_TEMPLATE_FROM_VOLUME_PATH = "/sharedmountpointprimarystorage/createtemplatefromvolume"
SMP_COMMIT_BITS_TO_IMAGESTORE_PATH = "/sharedmountpointprimarystorage/imagestore/commit"
SMP_UPLOAD_BITS_TO_IMAGESTORE_PATH = "/sharedmountpointprimarystorage/imagestore/upload"
LOCAL_UPLOAD_BIT_PATH = "/localstorage/sftp/upload"
NFS_UPLOAD_TO_SFTP_PATH = "/nfsprimarystorage/uploadtosftpbackupstorage"
SMP_UPLOAD_BITS_TO_SFTP_BACKUPSTORAGE_PATH = "/sharedmountpointprimarystorage/sftp/upload"
SBLK_CREATE_TEMPLATE_FROM_VOLUME_PATH = "/sharedblock/createtemplatefromvolume"
SBLK_COMMIT_BITS_TO_IMAGESTORE_PATH = "/sharedblock/imagestore/commit"
SBLK_UPLOAD_BITS_TO_IMAGESTORE_PATH = "/sharedblock/imagestore/upload"
CEPH_DOWNLOAD_IMAGE_PATH = "/ceph/backupstorage/image/download"
IMAGESTORE_IMPORT = "/imagestore/import/"
SFTP_DOWNLOAD_IMAGE_PATH = "/sftpbackupstorage/download"
KVM_MIGRATE_VM_PATH = "/vm/migrate"
GET_MD5_PATH = "/localstorage/getmd5"
CHECK_MD5_PATH = "/localstorage/checkmd5"
COPY_TO_REMOTE_BITS_PATH = "/localstorage/copytoremote"

test_stub = test_lib.lib_get_test_stub('mn_ha2')

def add_ps_network_gateway_sys_tag():
    '''
    This function currently only support 1 NFS storage separation.
    TODO:
        Fix for multiple ps and other type of storage network separation support
    '''

    pss = res_ops.query_resource(res_ops.PRIMARY_STORAGE)
    if len(pss) > 1:
        test_util.test_logger("add ps gateway skip for multiple ps case.")
        return

    ps = pss[0]
    if ps.type == "NFS":
        test_util.test_logger("add system tag: resourceUuid=%s tag=%s" %(ps.uuid, "primaryStorage::gateway::cidr::10.0.0.1/8"))
        tag_ops.create_system_tag('PrimaryStorageVO', ps.uuid, "primaryStorage::gateway::cidr::10.0.0.1/8")
    else:
        test_util.test_logger("add ps gateway skip for not other ps type case.")

    

USER_PATH = os.path.expanduser('~')
EXTRA_SUITE_SETUP_SCRIPT = '%s/.zstackwoodpecker/extra_suite_setup_config.sh' % USER_PATH
EXTRA_HOST_SETUP_SCRIPT = '%s/.zstackwoodpecker/extra_host_setup_config.sh' % USER_PATH

def test():
    if os.environ.get('ZSTACK_SIMULATOR') == "yes":
        os.system('pkill -f ./test_rest_server.py')
        process = subprocess.Popen("./test_rest_server.py", cwd=os.environ.get('woodpecker_root_path')+'/dailytest/', universal_newlines=True, preexec_fn=os.setsid)
        test_lib.setup_plan.execute_plan_without_deploy_test_agent()
        deploy_operations.deploy_simulator_database(test_lib.deploy_config, test_lib.all_scenario_config, test_lib.scenario_file)
        deploy_operations.deploy_initial_database(test_lib.deploy_config, test_lib.all_scenario_config, test_lib.scenario_file)
    
        agent_url = CP_PATH
        script = '''
        { entity -> 
        	slurper = new groovy.json.JsonSlurper();
        	entity_body_json = slurper.parseText(entity.body);
                src_path = entity_body_json["srcPath"].split('/')[3].split('@')[0]
        	def get = new URL("http://127.0.0.1:8888/test/api/v1.0/store/"+src_path).openConnection(); 
        	get.setRequestMethod("GET");
        	def getRC = get.getResponseCode();
        	if (!getRC.equals(200)) {
        		return;
        		//throw new Exception("shuang")
        	}; 
        	reply = get.getInputStream().getText();
                reply_json = slurper.parseText(reply);
                try {
        	        item = reply_json['result']
                	item_json = slurper.parseText(item);
        		action = item_json['%s']
                } catch(Exception ex) {
        		return
        	}
        	if (action == 1) {
        		sleep((24*60*60-60)*1000)
        	} else if (action == 2) {
        		sleep(360*1000)
        	}
        }
        ''' % (agent_url)
        deploy_operations.remove_simulator_agent_script(agent_url)
        deploy_operations.deploy_simulator_agent_script(agent_url, script)
        
        agent_url = CREATE_SNAPSHOT_PATH
        script = '''
        { entity -> 
        	slurper = new groovy.json.JsonSlurper();
        	entity_body_json = slurper.parseText(entity.body);
                volume_uuid = entity_body_json["volumeUuid"]
        	def get = new URL("http://127.0.0.1:8888/test/api/v1.0/store/"+volume_uuid).openConnection(); 
        	get.setRequestMethod("GET");
        	def getRC = get.getResponseCode();
        	if (!getRC.equals(200)) {
        		return;
        		//throw new Exception("shuang")
        	}; 
        	reply = get.getInputStream().getText();
                reply_json = slurper.parseText(reply);
                try {
        	        item = reply_json['result']
                	item_json = slurper.parseText(item);
        		action = item_json['%s']
                } catch(Exception ex) {
        		return
        	}
        	if (action == 1) {
        		sleep((24*60*60-60)*1000)
        	} else if (action == 2) {
        		sleep(360*1000)
        	}
        }
        ''' % (agent_url)
        deploy_operations.remove_simulator_agent_script(agent_url)
        deploy_operations.deploy_simulator_agent_script(agent_url, script)
        
        agent_url = UPLOAD_IMAGESTORE_PATH
        script = '''
        { entity -> 
        	slurper = new groovy.json.JsonSlurper();
        	entity_body_json = slurper.parseText(entity.body);
                src_path = entity_body_json["srcPath"].split('/')[3].split('@')[0]
        	def get = new URL("http://127.0.0.1:8888/test/api/v1.0/store/"+src_path).openConnection(); 
        	get.setRequestMethod("GET");
        	def getRC = get.getResponseCode();
        	if (!getRC.equals(200)) {
        		return;
        		//throw new Exception("shuang")
        	}; 
        	reply = get.getInputStream().getText();
                reply_json = slurper.parseText(reply);
                try {
        	        item = reply_json['result']
                	item_json = slurper.parseText(item);
        		action = item_json['%s']
                } catch(Exception ex) {
        		return
        	}
        	if (action == 1) {
        		sleep((24*60*60-60)*1000)
        	} else if (action == 2) {
        		sleep(360*1000)
        	}
        }
        ''' % (agent_url)
        deploy_operations.remove_simulator_agent_script(agent_url)
        deploy_operations.deploy_simulator_agent_script(agent_url, script)
        
        agent_url = NFS_CREATE_TEMPLATE_FROM_VOLUME_PATH
        script = '''
        { entity -> 
        	slurper = new groovy.json.JsonSlurper();
        	entity_body_json = slurper.parseText(entity.body);
                src_path = entity_body_json["rootVolumePath"].split('vol-')[1].split('/')[0]
        	def get = new URL("http://127.0.0.1:8888/test/api/v1.0/store/"+src_path).openConnection(); 
        	get.setRequestMethod("GET");
        	def getRC = get.getResponseCode();
        	if (!getRC.equals(200)) {
        		return;
        		//throw new Exception("shuang")
        	}; 
        	reply = get.getInputStream().getText();
                reply_json = slurper.parseText(reply);
                try {
        	        item = reply_json['result']
                	item_json = slurper.parseText(item);
        		action = item_json['%s']
                } catch(Exception ex) {
        		return
        	}
        	if (action == 1) {
        		sleep((24*60*60-60)*1000)
        	} else if (action == 2) {
        		sleep(360*1000)
        	}
        }
        ''' % (agent_url)
        deploy_operations.remove_simulator_agent_script(agent_url)
        deploy_operations.deploy_simulator_agent_script(agent_url, script)
        
        agent_url = SMP_CREATE_TEMPLATE_FROM_VOLUME_PATH
        script = '''
        { entity -> 
        	slurper = new groovy.json.JsonSlurper();
        	entity_body_json = slurper.parseText(entity.body);
                src_path = entity_body_json["volumePath"].split('vol-')[1].split('/')[0]
        	def get = new URL("http://127.0.0.1:8888/test/api/v1.0/store/"+src_path).openConnection(); 
        	get.setRequestMethod("GET");
        	def getRC = get.getResponseCode();
        	if (!getRC.equals(200)) {
        		return;
        		//throw new Exception("shuang")
        	}; 
        	reply = get.getInputStream().getText();
                reply_json = slurper.parseText(reply);
                try {
        	        item = reply_json['result']
                	item_json = slurper.parseText(item);
        		action = item_json['%s']
                } catch(Exception ex) {
        		return
        	}
        	if (action == 1) {
        		sleep((24*60*60-60)*1000)
        	} else if (action == 2) {
        		sleep(360*1000)
        	}
        }
        ''' % (agent_url)
        deploy_operations.remove_simulator_agent_script(agent_url)
        deploy_operations.deploy_simulator_agent_script(agent_url, script)
        
        agent_url = NFS_COMMIT_TO_IMAGESTORE_PATH
        script = '''
        { entity -> 
        	slurper = new groovy.json.JsonSlurper();
        	entity_body_json = slurper.parseText(entity.body);
                image_uuid = entity_body_json["imageUuid"]
        	def get = new URL("http://127.0.0.1:8888/test/api/v1.0/store/"+image_uuid).openConnection(); 
        	get.setRequestMethod("GET");
        	def getRC = get.getResponseCode();
        	if (!getRC.equals(200)) {
        		return;
        		//throw new Exception("shuang")
        	}; 
        	reply = get.getInputStream().getText();
                reply_json = slurper.parseText(reply);
                try {
        	        item = reply_json['result']
                	item_json = slurper.parseText(item);
        		action = item_json['%s']
                } catch(Exception ex) {
        		return
        	}
        	if (action == 1) {
        		sleep((24*60*60-60)*1000)
        	} else if (action == 2) {
        		sleep(360*1000)
        	}
        }
        ''' % (agent_url)
        deploy_operations.remove_simulator_agent_script(agent_url)
        deploy_operations.deploy_simulator_agent_script(agent_url, script)
        
        agent_url = SMP_COMMIT_BITS_TO_IMAGESTORE_PATH
        script = '''
        { entity -> 
        	slurper = new groovy.json.JsonSlurper();
        	entity_body_json = slurper.parseText(entity.body);
                image_uuid = entity_body_json["imageUuid"]
        	def get = new URL("http://127.0.0.1:8888/test/api/v1.0/store/"+image_uuid).openConnection(); 
        	get.setRequestMethod("GET");
        	def getRC = get.getResponseCode();
        	if (!getRC.equals(200)) {
        		return;
        		//throw new Exception("shuang")
        	}; 
        	reply = get.getInputStream().getText();
                reply_json = slurper.parseText(reply);
                try {
        	        item = reply_json['result']
                	item_json = slurper.parseText(item);
        		action = item_json['%s']
                } catch(Exception ex) {
        		return
        	}
        	if (action == 1) {
        		sleep((24*60*60-60)*1000)
        	} else if (action == 2) {
        		sleep(360*1000)
        	}
        }
        ''' % (agent_url)
        
        deploy_operations.remove_simulator_agent_script(agent_url)
        deploy_operations.deploy_simulator_agent_script(agent_url, script)
        
        
        agent_url = NFS_UPLOAD_TO_IMAGESTORE_PATH
        script = '''
        { entity -> 
        	slurper = new groovy.json.JsonSlurper();
        	entity_body_json = slurper.parseText(entity.body);
                image_uuid = entity_body_json["imageUuid"]
        	def get = new URL("http://127.0.0.1:8888/test/api/v1.0/store/"+image_uuid).openConnection(); 
        	get.setRequestMethod("GET");
        	def getRC = get.getResponseCode();
        	if (!getRC.equals(200)) {
        		return;
        		//throw new Exception("shuang")
        	}; 
        	reply = get.getInputStream().getText();
                reply_json = slurper.parseText(reply);
                try {
        	        item = reply_json['result']
                	item_json = slurper.parseText(item);
        		action = item_json['%s']
                } catch(Exception ex) {
        		return
        	}
        	if (action == 1) {
        		sleep((24*60*60-60)*1000)
        	} else if (action == 2) {
        		sleep(360*1000)
        	}
        }
        ''' % (agent_url)
        deploy_operations.remove_simulator_agent_script(agent_url)
        deploy_operations.deploy_simulator_agent_script(agent_url, script)
        
        agent_url = SMP_UPLOAD_BITS_TO_IMAGESTORE_PATH
        script = '''
        { entity -> 
        	slurper = new groovy.json.JsonSlurper();
        	entity_body_json = slurper.parseText(entity.body);
                image_uuid = entity_body_json["imageUuid"]
        	def get = new URL("http://127.0.0.1:8888/test/api/v1.0/store/"+image_uuid).openConnection(); 
        	get.setRequestMethod("GET");
        	def getRC = get.getResponseCode();
        	if (!getRC.equals(200)) {
        		return;
        		//throw new Exception("shuang")
        	}; 
        	reply = get.getInputStream().getText();
                reply_json = slurper.parseText(reply);
                try {
        	        item = reply_json['result']
                	item_json = slurper.parseText(item);
        		action = item_json['%s']
                } catch(Exception ex) {
        		return
        	}
        	if (action == 1) {
        		sleep((24*60*60-60)*1000)
        	} else if (action == 2) {
        		sleep(360*1000)
        	}
        }
        ''' % (agent_url)
        
        deploy_operations.remove_simulator_agent_script(agent_url)
        deploy_operations.deploy_simulator_agent_script(agent_url, script)
        
        agent_url = LOCAL_CREATE_TEMPLATE_FROM_VOLUME
        script = '''
        { entity -> 
        	slurper = new groovy.json.JsonSlurper();
        	entity_body_json = slurper.parseText(entity.body);
                volume_uuid = entity_body_json["volumePath"].split('vol-')[1].split('/')[0]
        	def get = new URL("http://127.0.0.1:8888/test/api/v1.0/store/"+volume_uuid).openConnection(); 
        	get.setRequestMethod("GET");
        	def getRC = get.getResponseCode();
        	if (!getRC.equals(200)) {
        		return;
        		//throw new Exception("shuang")
        	}; 
        	reply = get.getInputStream().getText();
                reply_json = slurper.parseText(reply);
                try {
        	        item = reply_json['result']
                	item_json = slurper.parseText(item);
        		action = item_json['%s']
                } catch(Exception ex) {
        		return
        	}
        	if (action == 1) {
        		sleep((24*60*60-60)*1000)
        	} else if (action == 2) {
        		sleep(360*1000)
        	}
        }
        ''' % (agent_url)
        deploy_operations.remove_simulator_agent_script(agent_url)
        deploy_operations.deploy_simulator_agent_script(agent_url, script)
        
        agent_url = LOCAL_COMMIT_TO_IMAGESTORE_PATH
        script = '''
        { entity -> 
        	slurper = new groovy.json.JsonSlurper();
        	entity_body_json = slurper.parseText(entity.body);
                image_uuid = entity_body_json["imageUuid"]
        	def get = new URL("http://127.0.0.1:8888/test/api/v1.0/store/"+image_uuid).openConnection(); 
        	get.setRequestMethod("GET");
        	def getRC = get.getResponseCode();
        	if (!getRC.equals(200)) {
        		return;
        		//throw new Exception("shuang")
        	}; 
        	reply = get.getInputStream().getText();
                reply_json = slurper.parseText(reply);
                try {
        	        item = reply_json['result']
                	item_json = slurper.parseText(item);
        		action = item_json['%s']
                } catch(Exception ex) {
        		return
        	}
        	if (action == 1) {
        		sleep((24*60*60-60)*1000)
        	} else if (action == 2) {
        		sleep(360*1000)
        	}
        }
        ''' % (agent_url)
        deploy_operations.remove_simulator_agent_script(agent_url)
        deploy_operations.deploy_simulator_agent_script(agent_url, script)
        
        
        agent_url = LOCAL_UPLOAD_TO_IMAGESTORE_PATH
        script = '''
        { entity -> 
        	slurper = new groovy.json.JsonSlurper();
        	entity_body_json = slurper.parseText(entity.body);
                image_uuid = entity_body_json["imageUuid"]
        	def get = new URL("http://127.0.0.1:8888/test/api/v1.0/store/"+image_uuid).openConnection(); 
        	get.setRequestMethod("GET");
        	def getRC = get.getResponseCode();
        	if (!getRC.equals(200)) {
        		return;
        		//throw new Exception("shuang")
        	}; 
        	reply = get.getInputStream().getText();
                reply_json = slurper.parseText(reply);
                try {
        	        item = reply_json['result']
                	item_json = slurper.parseText(item);
        		action = item_json['%s']
                } catch(Exception ex) {
        		return
        	}
        	if (action == 1) {
        		sleep((24*60*60-60)*1000)
        	} else if (action == 2) {
        		sleep(360*1000)
        	}
        }
        ''' % (agent_url)
        deploy_operations.remove_simulator_agent_script(agent_url)
        deploy_operations.deploy_simulator_agent_script(agent_url, script)
        
        agent_url = KVM_TAKE_VOLUME_SNAPSHOT_PATH
        script = '''
        { entity -> 
        	slurper = new groovy.json.JsonSlurper();
        	entity_body_json = slurper.parseText(entity.body);
                volume_uuid = entity_body_json["volumeUuid"]
        	def get = new URL("http://127.0.0.1:8888/test/api/v1.0/store/"+volume_uuid).openConnection(); 
        	get.setRequestMethod("GET");
        	def getRC = get.getResponseCode();
        	if (!getRC.equals(200)) {
        		return;
        		//throw new Exception("shuang")
        	}; 
        	reply = get.getInputStream().getText();
                reply_json = slurper.parseText(reply);
                try {
        	        item = reply_json['result']
                	item_json = slurper.parseText(item);
        		action = item_json['%s']
                } catch(Exception ex) {
        		return
        	}
        	if (action == 1) {
        		sleep((24*60*60-60)*1000)
        	} else if (action == 2) {
        		sleep(360*1000)
        	}
        }
        ''' % (agent_url)
        deploy_operations.remove_simulator_agent_script(agent_url)
        deploy_operations.deploy_simulator_agent_script(agent_url, script)
        
        agent_url = LOCAL_UPLOAD_BIT_PATH
        script = '''
        { entity -> 
        	slurper = new groovy.json.JsonSlurper();
        	entity_body_json = slurper.parseText(entity.body);
                src_path = entity_body_json["primaryStorageInstallPath"].split('image-')[1].split('/')[0]
        	def get = new URL("http://127.0.0.1:8888/test/api/v1.0/store/"+src_path).openConnection(); 
        	get.setRequestMethod("GET");
        	def getRC = get.getResponseCode();
        	if (!getRC.equals(200)) {
        		return;
        		//throw new Exception("shuang")
        	}; 
        	reply = get.getInputStream().getText();
                reply_json = slurper.parseText(reply);
                try {
        	        item = reply_json['result']
                	item_json = slurper.parseText(item);
        		action = item_json['%s']
                } catch(Exception ex) {
        		return
        	}
        	if (action == 1) {
        		sleep((24*60*60-60)*1000)
        	} else if (action == 2) {
        		sleep(360*1000)
        	}
        }
        ''' % (agent_url)
        deploy_operations.remove_simulator_agent_script(agent_url)
        deploy_operations.deploy_simulator_agent_script(agent_url, script)
        
        agent_url = NFS_UPLOAD_TO_SFTP_PATH
        script = '''
        { entity -> 
        	slurper = new groovy.json.JsonSlurper();
        	entity_body_json = slurper.parseText(entity.body);
                src_path = entity_body_json["primaryStorageInstallPath"].split('image-')[1].split('/')[0]
        	def get = new URL("http://127.0.0.1:8888/test/api/v1.0/store/"+src_path).openConnection(); 
        	get.setRequestMethod("GET");
        	def getRC = get.getResponseCode();
        	if (!getRC.equals(200)) {
        		return;
        		//throw new Exception("shuang")
        	}; 
        	reply = get.getInputStream().getText();
                reply_json = slurper.parseText(reply);
                try {
        	        item = reply_json['result']
                	item_json = slurper.parseText(item);
        		action = item_json['%s']
                } catch(Exception ex) {
        		return
        	}
        	if (action == 1) {
        		sleep((24*60*60-60)*1000)
        	} else if (action == 2) {
        		sleep(360*1000)
        	}
        }
        ''' % (agent_url)
        deploy_operations.remove_simulator_agent_script(agent_url)
        deploy_operations.deploy_simulator_agent_script(agent_url, script)
        
        agent_url = SMP_UPLOAD_BITS_TO_SFTP_BACKUPSTORAGE_PATH
        script = '''
        { entity -> 
        	slurper = new groovy.json.JsonSlurper();
        	entity_body_json = slurper.parseText(entity.body);
                src_path = entity_body_json["primaryStorageInstallPath"].split('image-')[1].split('/')[0]
        	def get = new URL("http://127.0.0.1:8888/test/api/v1.0/store/"+src_path).openConnection(); 
        	get.setRequestMethod("GET");
        	def getRC = get.getResponseCode();
        	if (!getRC.equals(200)) {
        		return;
        		//throw new Exception("shuang")
        	}; 
        	reply = get.getInputStream().getText();
                reply_json = slurper.parseText(reply);
                try {
        	        item = reply_json['result']
                	item_json = slurper.parseText(item);
        		action = item_json['%s']
                } catch(Exception ex) {
        		return
        	}
        	if (action == 1) {
        		sleep((24*60*60-60)*1000)
        	} else if (action == 2) {
        		sleep(360*1000)
        	}
        }
        ''' % (agent_url)
        deploy_operations.remove_simulator_agent_script(agent_url)
        deploy_operations.deploy_simulator_agent_script(agent_url, script)
        
        agent_url = SBLK_CREATE_TEMPLATE_FROM_VOLUME_PATH
        script = '''
        { entity -> 
        	slurper = new groovy.json.JsonSlurper();
        	entity_body_json = slurper.parseText(entity.body);
                volume_uuid = entity_body_json["volumePath"].split('/')[3]
        	def get = new URL("http://127.0.0.1:8888/test/api/v1.0/store/"+volume_uuid).openConnection(); 
        	get.setRequestMethod("GET");
        	def getRC = get.getResponseCode();
        	if (!getRC.equals(200)) {
        		return;
        		//throw new Exception("shuang")
        	}; 
        	reply = get.getInputStream().getText();
                reply_json = slurper.parseText(reply);
                try {
        	        item = reply_json['result']
                	item_json = slurper.parseText(item);
        		action = item_json['%s']
                } catch(Exception ex) {
        		return
        	}
        	if (action == 1) {
        		sleep((24*60*60-60)*1000)
        	} else if (action == 2) {
        		sleep(360*1000)
        	}
        }
        ''' % (agent_url)
        deploy_operations.remove_simulator_agent_script(agent_url)
        deploy_operations.deploy_simulator_agent_script(agent_url, script)
        
        agent_url = SBLK_COMMIT_BITS_TO_IMAGESTORE_PATH
        script = '''
        { entity -> 
        	slurper = new groovy.json.JsonSlurper();
        	entity_body_json = slurper.parseText(entity.body);
                image_uuid = entity_body_json["imageUuid"]
        	def get = new URL("http://127.0.0.1:8888/test/api/v1.0/store/"+image_uuid).openConnection(); 
        	get.setRequestMethod("GET");
        	def getRC = get.getResponseCode();
        	if (!getRC.equals(200)) {
        		return;
        		//throw new Exception("shuang")
        	}; 
        	reply = get.getInputStream().getText();
                reply_json = slurper.parseText(reply);
                try {
        	        item = reply_json['result']
                	item_json = slurper.parseText(item);
        		action = item_json['%s']
                } catch(Exception ex) {
        		return
        	}
        	if (action == 1) {
        		sleep((24*60*60-60)*1000)
        	} else if (action == 2) {
        		sleep(360*1000)
        	}
        }
        ''' % (agent_url)
        
        deploy_operations.remove_simulator_agent_script(agent_url)
        deploy_operations.deploy_simulator_agent_script(agent_url, script)
        
        
        agent_url = SBLK_UPLOAD_BITS_TO_IMAGESTORE_PATH
        script = '''
        { entity -> 
        	slurper = new groovy.json.JsonSlurper();
        	entity_body_json = slurper.parseText(entity.body);
                image_uuid = entity_body_json["imageUuid"]
        	def get = new URL("http://127.0.0.1:8888/test/api/v1.0/store/"+image_uuid).openConnection(); 
        	get.setRequestMethod("GET");
        	def getRC = get.getResponseCode();
        	if (!getRC.equals(200)) {
        		return;
        		//throw new Exception("shuang")
        	}; 
        	reply = get.getInputStream().getText();
                reply_json = slurper.parseText(reply);
                try {
        	        item = reply_json['result']
                	item_json = slurper.parseText(item);
        		action = item_json['%s']
                } catch(Exception ex) {
        		return
        	}
        	if (action == 1) {
        		sleep((24*60*60-60)*1000)
        	} else if (action == 2) {
        		sleep(360*1000)
        	}
        }
        ''' % (agent_url)
        
        deploy_operations.remove_simulator_agent_script(agent_url)
        deploy_operations.deploy_simulator_agent_script(agent_url, script)
        
        agent_url = CEPH_DOWNLOAD_IMAGE_PATH
        script = '''
        { entity -> 
        	slurper = new groovy.json.JsonSlurper();
        	entity_body_json = slurper.parseText(entity.body);
                image_uuid = entity_body_json["imageUuid"]
        	def get = new URL("http://127.0.0.1:8888/test/api/v1.0/store/"+image_uuid).openConnection(); 
        	get.setRequestMethod("GET");
        	def getRC = get.getResponseCode();
        	if (!getRC.equals(200)) {
        		return;
        		//throw new Exception("shuang")
        	}; 
        	reply = get.getInputStream().getText();
                reply_json = slurper.parseText(reply);
                try {
        	        item = reply_json['result']
                	item_json = slurper.parseText(item);
        		action = item_json['%s']
                } catch(Exception ex) {
        		return
        	}
        	if (action == 1) {
        		sleep((24*60*60-60)*1000)
        	} else if (action == 2) {
        		sleep(360*1000)
        	}
        }
        ''' % (agent_url)
        deploy_operations.remove_simulator_agent_script(agent_url)
        deploy_operations.deploy_simulator_agent_script(agent_url, script)
        
        agent_url = IMAGESTORE_IMPORT
        script = '''
        { entity -> 
        	slurper = new groovy.json.JsonSlurper();
        	entity_body_json = slurper.parseText(entity.body);
                image_uuid = entity_body_json["imageuuid"]
        	def get = new URL("http://127.0.0.1:8888/test/api/v1.0/store/"+image_uuid).openConnection(); 
        	get.setRequestMethod("GET");
        	def getRC = get.getResponseCode();
        	if (!getRC.equals(200)) {
        		return;
        		//throw new Exception("shuang")
        	}; 
        	reply = get.getInputStream().getText();
                reply_json = slurper.parseText(reply);
                try {
        	        item = reply_json['result']
                	item_json = slurper.parseText(item);
        		action = item_json['%s']
                } catch(Exception ex) {
        		return
        	}
        	if (action == 1) {
        		sleep((24*60*60-60)*1000)
        	} else if (action == 2) {
        		sleep(360*1000)
        	}
        }
        ''' % (agent_url)
        deploy_operations.remove_simulator_agent_script(agent_url)
        deploy_operations.deploy_simulator_agent_script(agent_url, script)
        
        agent_url = SFTP_DOWNLOAD_IMAGE_PATH
        script = '''
        { entity -> 
        	slurper = new groovy.json.JsonSlurper();
        	entity_body_json = slurper.parseText(entity.body);
                image_uuid = entity_body_json["imageUuid"]
        	def get = new URL("http://127.0.0.1:8888/test/api/v1.0/store/"+image_uuid).openConnection(); 
        	get.setRequestMethod("GET");
        	def getRC = get.getResponseCode();
        	if (!getRC.equals(200)) {
        		return;
        		//throw new Exception("shuang")
        	}; 
        	reply = get.getInputStream().getText();
                reply_json = slurper.parseText(reply);
                try {
        	        item = reply_json['result']
                	item_json = slurper.parseText(item);
        		action = item_json['%s']
                } catch(Exception ex) {
        		return
        	}
        	if (action == 1) {
        		sleep((24*60*60-60)*1000)
        	} else if (action == 2) {
        		sleep(360*1000)
        	}
        }
        ''' % (agent_url)
        deploy_operations.remove_simulator_agent_script(agent_url)
        deploy_operations.deploy_simulator_agent_script(agent_url, script)
        
        agent_url = KVM_MIGRATE_VM_PATH
        script = '''
        { entity -> 
        	slurper = new groovy.json.JsonSlurper();
        	entity_body_json = slurper.parseText(entity.body);
                vm_uuid = entity_body_json["vmUuid"]
        	def get = new URL("http://127.0.0.1:8888/test/api/v1.0/store/"+vm_uuid).openConnection(); 
        	get.setRequestMethod("GET");
        	def getRC = get.getResponseCode();
        	if (!getRC.equals(200)) {
        		return;
        		//throw new Exception("shuang")
        	}; 
        	reply = get.getInputStream().getText();
                reply_json = slurper.parseText(reply);
                try {
        	        item = reply_json['result']
                	item_json = slurper.parseText(item);
        		action = item_json['%s']
                } catch(Exception ex) {
        		return
        	}
        	if (action == 1) {
        		sleep((24*60*60-60)*1000)
        	} else if (action == 2) {
        		sleep(360*1000)
        	}
        }
        ''' % (agent_url)
        deploy_operations.remove_simulator_agent_script(agent_url)
        deploy_operations.deploy_simulator_agent_script(agent_url, script)
        
        agent_url = GET_MD5_PATH
        script = '''
        { entity -> 
        	slurper = new groovy.json.JsonSlurper();
        	entity_body_json = slurper.parseText(entity.body);
                volume_uuid = entity_body_json["volumeUuid"]
        	def get = new URL("http://127.0.0.1:8888/test/api/v1.0/store/"+volume_uuid).openConnection(); 
        	get.setRequestMethod("GET");
        	def getRC = get.getResponseCode();
        	if (!getRC.equals(200)) {
        		return;
        		//throw new Exception("shuang")
        	}; 
        	reply = get.getInputStream().getText();
                reply_json = slurper.parseText(reply);
                try {
        	        item = reply_json['result']
                	item_json = slurper.parseText(item);
        		action = item_json['%s']
                } catch(Exception ex) {
        		return
        	}
        	if (action == 1) {
        		sleep((24*60*60-60)*1000)
        	} else if (action == 2) {
        		sleep(360*1000)
        	}
        }
        ''' % (agent_url)
        deploy_operations.remove_simulator_agent_script(agent_url)
        deploy_operations.deploy_simulator_agent_script(agent_url, script)
        
        agent_url = CHECK_MD5_PATH
        script = '''
        { entity -> 
        	slurper = new groovy.json.JsonSlurper();
        	entity_body_json = slurper.parseText(entity.body);
                volume_uuid = entity_body_json["volumeUuid"]
        	def get = new URL("http://127.0.0.1:8888/test/api/v1.0/store/"+volume_uuid).openConnection(); 
        	get.setRequestMethod("GET");
        	def getRC = get.getResponseCode();
        	if (!getRC.equals(200)) {
        		return;
        		//throw new Exception("shuang")
        	}; 
        	reply = get.getInputStream().getText();
                reply_json = slurper.parseText(reply);
                try {
        	        item = reply_json['result']
                	item_json = slurper.parseText(item);
        		action = item_json['%s']
                } catch(Exception ex) {
        		return
        	}
        	if (action == 1) {
        		sleep((24*60*60-60)*1000)
        	} else if (action == 2) {
        		sleep(360*1000)
        	}
        }
        ''' % (agent_url)
        deploy_operations.remove_simulator_agent_script(agent_url)
        deploy_operations.deploy_simulator_agent_script(agent_url, script)
        
        agent_url = COPY_TO_REMOTE_BITS_PATH
        script = '''
        { entity -> 
        	slurper = new groovy.json.JsonSlurper();
        	entity_body_json = slurper.parseText(entity.body);
                volume_uuid = entity_body_json["paths"][0].split('vol-')[1].split('/')[0]
        	def get = new URL("http://127.0.0.1:8888/test/api/v1.0/store/"+volume_uuid).openConnection(); 
        	get.setRequestMethod("GET");
        	def getRC = get.getResponseCode();
        	if (!getRC.equals(200)) {
        		return;
        		//throw new Exception("shuang")
        	}; 
        	reply = get.getInputStream().getText();
                reply_json = slurper.parseText(reply);
                try {
        	        item = reply_json['result']
                	item_json = slurper.parseText(item);
        		action = item_json['%s']
                } catch(Exception ex) {
        		return
        	}
        	if (action == 1) {
        		sleep((24*60*60-60)*1000)
        	} else if (action == 2) {
        		sleep(360*1000)
        	}
        }
        ''' % (agent_url)
        deploy_operations.remove_simulator_agent_script(agent_url)
        deploy_operations.deploy_simulator_agent_script(agent_url, script)
        deploy_operations.install_mini_server()
    else:
        if test_lib.scenario_config == None or test_lib.scenario_file ==None:
            test_util.test_fail('Suite Setup Fail without scenario')
    
        if test_lib.scenario_config != None and test_lib.scenario_file != None and not os.path.exists(test_lib.scenario_file):
            scenario_operations.deploy_scenario(test_lib.all_scenario_config, test_lib.scenario_file, test_lib.deploy_config)
            test_util.test_skip('Suite Setup Success')
        if test_lib.scenario_config != None and test_lib.scenario_destroy != None:
            scenario_operations.destroy_scenario(test_lib.all_scenario_config, test_lib.scenario_destroy)
    
        nic_name = "eth0"
        if test_lib.scenario_config != None and test_lib.scenario_file != None and os.path.exists(test_lib.scenario_file):
            nic_name = "zsn0"
    
        #This vlan creation is not a must, if testing is under nested virt env. But it is required on physical host without enough physcial network devices and your test execution machine is not the same one as Host machine. 
        #no matter if current host is a ZStest host, we need to create 2 vlan devs for future testing connection for novlan test cases.
        linux.create_vlan_eth(nic_name, 10)
        linux.create_vlan_eth(nic_name, 11)
    
        #If test execution machine is not the same one as Host machine, deploy work is needed to separated to 2 steps(deploy_test_agent, execute_plan_without_deploy_test_agent). And it can not directly call SetupAction.run()
        test_lib.setup_plan.deploy_test_agent()
        cmd = host_plugin.CreateVlanDeviceCmd()
        cmd.ethname = nic_name
        cmd.vlan = 10
        
        cmd2 = host_plugin.CreateVlanDeviceCmd()
        cmd2.ethname = nic_name
        cmd2.vlan = 11
        testHosts = test_lib.lib_get_all_hosts_from_plan()
        if type(testHosts) != type([]):
            testHosts = [testHosts]
        for host in testHosts:
            http.json_dump_post(testagent.build_http_path(host.managementIp_, host_plugin.CREATE_VLAN_DEVICE_PATH), cmd)
            http.json_dump_post(testagent.build_http_path(host.managementIp_, host_plugin.CREATE_VLAN_DEVICE_PATH), cmd2)
    
    
        test_stub.deploy_2ha(test_lib.all_scenario_config, test_lib.scenario_file, test_lib.deploy_config)
        mn_ip1 = test_stub.get_host_by_index_in_scenario_file(test_lib.all_scenario_config, test_lib.scenario_file, 0).ip_
        mn_ip2 = test_stub.get_host_by_index_in_scenario_file(test_lib.all_scenario_config, test_lib.scenario_file, 1).ip_
    
        if not xmlobject.has_element(test_lib.deploy_config, 'backupStorages.miniBackupStorage'):
            host_ip1 = test_stub.get_host_by_index_in_scenario_file(test_lib.all_scenario_config, test_lib.scenario_file, 2).ip_
            test_stub.recover_vlan_in_host(host_ip1, test_lib.all_scenario_config, test_lib.deploy_config)
    
        test_stub.wrapper_of_wait_for_management_server_start(600, EXTRA_SUITE_SETUP_SCRIPT)
        test_util.test_logger("@@@DEBUG->suite_setup@@@ os\.environ\[\'ZSTACK_BUILT_IN_HTTP_SERVER_IP\'\]=%s; os\.environ\[\'zstackHaVip\'\]=%s"    \
                              %(os.environ['ZSTACK_BUILT_IN_HTTP_SERVER_IP'], os.environ['zstackHaVip']) )
        ssh.scp_file("/home/license-10host-10days-hp.txt", "/home/license-10host-10days-hp.txt", mn_ip1, 'root', 'password')
        ssh.scp_file("/home/license-10host-10days-hp.txt", "/home/license-10host-10days-hp.txt", mn_ip2, 'root', 'password')
        if os.path.exists(EXTRA_SUITE_SETUP_SCRIPT):
            os.system("bash %s %s" % (EXTRA_SUITE_SETUP_SCRIPT, mn_ip1))
            os.system("bash %s %s" % (EXTRA_SUITE_SETUP_SCRIPT, mn_ip2))
    
        deploy_operations.deploy_initial_database(test_lib.deploy_config, test_lib.all_scenario_config, test_lib.scenario_file)
        for host in testHosts:
            os.system("bash %s %s" % (EXTRA_HOST_SETUP_SCRIPT, host.managementIp_))
    
        test_lib.lib_set_primary_storage_imagecache_gc_interval(1)
        #test_lib.lib_set_reserved_memory('1G')
    
        if test_lib.lib_cur_cfg_is_a_and_b(["test-config-vyos-local-ps.xml"], ["scenario-config-upgrade-3.1.1.xml"]):
            cmd = r"sed -i '$a\172.20.198.8 rsync.repo.zstack.io' /etc/hosts"
            ssh.execute(cmd, mn_ip1, "root", "password", False, 22)
            ssh.execute(cmd, mn_ip2, "root", "password", False, 22)

    test_util.test_pass('Suite Setup Success')