'''

@author: Frank
'''

import os
import subprocess
import zstackwoodpecker.operations.scenario_operations as scenario_operations
import zstackwoodpecker.operations.deploy_operations as deploy_operations
import zstackwoodpecker.operations.config_operations as config_operations
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_util as test_util

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


USER_PATH = os.path.expanduser('~')
EXTRA_SUITE_SETUP_SCRIPT = '%s/.zstackwoodpecker/extra_suite_setup_config.sh' % USER_PATH
def test():
    os.system('pkill -f ./test_rest_server.py')
    process = subprocess.Popen("./test_rest_server.py", cwd=os.environ.get('woodpecker_root_path')+'/dailytest/', universal_newlines=True, preexec_fn=os.setsid)
    if test_lib.scenario_config != None and test_lib.scenario_file != None and not os.path.exists(test_lib.scenario_file):
        scenario_operations.deploy_scenario(test_lib.all_scenario_config, test_lib.scenario_file, test_lib.deploy_config)
        test_util.test_skip('Suite Setup Success')
    if test_lib.scenario_config != None and test_lib.scenario_destroy != None:
        scenario_operations.destroy_scenario(test_lib.all_scenario_config, test_lib.scenario_destroy)

    test_lib.setup_plan.execute_plan_without_deploy_test_agent()

    if test_lib.scenario_config != None and test_lib.scenario_file != None and os.path.exists(test_lib.scenario_file):
        mn_ips = deploy_operations.get_nodes_from_scenario_file(test_lib.all_scenario_config, test_lib.scenario_file, test_lib.deploy_config)
        if os.path.exists(EXTRA_SUITE_SETUP_SCRIPT):
            os.system("bash %s '%s' %s" % (EXTRA_SUITE_SETUP_SCRIPT, mn_ips,'project-management'))
    elif os.path.exists(EXTRA_SUITE_SETUP_SCRIPT):
        os.system("bash %s '' '%s'" % (EXTRA_SUITE_SETUP_SCRIPT,'project-management'))

    if os.environ.get('ZSTACK_SIMULATOR') == "yes":
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
        volume_uuid = entity_body_json["paths"].split('vol-')[1].split('/')[0]
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

    test_util.test_pass('Suite Setup Success')
