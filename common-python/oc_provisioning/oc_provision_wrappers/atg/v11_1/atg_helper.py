# The MIT License (MIT)
#
# Copyright (c) 2016 Oracle
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
__author__ = "Michael Shanley (Oracle A-Team)"
__copyright__ = "Copyright (c) 2016  Oracle and/or its affiliates. All rights reserved."
__version__ = "1.0.0.0"
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

from oc_provision_wrappers import commerce_setup_helper
import os
import logging

logger = logging.getLogger(__name__)

installer_key = 'atg'
json_key = 'ATG_install'
service_name = "ATG"
atg_binary_key = 'atg_binary'
crs_binary_key = 'crs_binary'
service_binary_key = 'service_binary'


def install_atg(configData, full_path): 
    
    if json_key in configData:
        jsonData = configData[json_key]
    else:
        logging.error(json_key + " config data missing from json. will not install")
        return False

    # get info from json on what version we are installing
    installer_config_data = commerce_setup_helper.get_installer_config_data(configData, full_path, installer_key)
    
    if (not installer_config_data):
        return False
    
    service_version = installer_config_data['service_version'] 
        
    logging.info("installing " + service_name)

    try:
        binary_path = installer_config_data[atg_binary_key]
    except KeyError:
        logging.error("Installer key " + atg_binary_key + " not found in config file.")
        return False

    if (not os.path.exists(binary_path)):
        logging.error("Cannot find installer file " + binary_path + "   Halting")
        return
        
    response_files_path = full_path + "/responseFiles/" + service_version
                         
    requiredFields = ['dynamoRoot', 'installOwner', 'installGroup', 'rmiPort', 'javaHome', 'wl_home', 'wl_domain', 'wl_adminPort', 'install_crs']
    commerce_setup_helper.check_required_fields(jsonData, requiredFields)

    INSTALL_DIR = jsonData['dynamoRoot']
    INSTALL_OWNER = jsonData['installOwner']
    INSTALL_GROUP = jsonData['installGroup']
    RMI_PORT = jsonData['rmiPort']
    JAVA_DIR = jsonData['javaHome']
    WL_HOME = jsonData['wl_home']
    WL_DOMAIN = jsonData['wl_domain']
    WL_ADMIN_PORT = jsonData['wl_adminPort']
    INSTALL_CRS = jsonData['install_crs']
    INSTALL_SERVICE = jsonData['install_service']
    
    field_replacements = {'INSTALL_HOME':INSTALL_DIR, 'WEBLOGIC_HOME':WL_HOME, 'WEBLOGIC_DOMAIN':WL_DOMAIN, 'WEBLOGIC_ADMIN_PORT':WL_ADMIN_PORT, 'ATGRMI_PORT':RMI_PORT, 'JDK_PATH':JAVA_DIR}
    commerce_setup_helper.substitute_file_fields(response_files_path + '/linux/installer.properties.master', response_files_path + '/linux/installer.properties', field_replacements)
    
    # make the install tree with correct owner if needed
    commerce_setup_helper.mkdir_with_perms(INSTALL_DIR, INSTALL_OWNER, INSTALL_GROUP)
    
    installCommand = "\"" + binary_path + " -i silent -f " + response_files_path + "/linux/installer.properties" + "\"" 
    commerce_setup_helper.exec_as_user(INSTALL_OWNER, installCommand)
    
    commerce_setup_helper.add_to_bashrc(INSTALL_OWNER, "##################### \n")
    commerce_setup_helper.add_to_bashrc(INSTALL_OWNER, "#ATG Settings \n")
    commerce_setup_helper.add_to_bashrc(INSTALL_OWNER, "##################### \n")
    commerce_setup_helper.add_to_bashrc(INSTALL_OWNER, "export DYNAMO_ROOT=" + INSTALL_DIR + "\n")
    commerce_setup_helper.add_to_bashrc(INSTALL_OWNER, "export DYNAMO_HOME=$DYNAMO_ROOT/home \n\n")

    if (INSTALL_CRS == "true"):
        
        logging.info("installing CRS")
        
        crs_binary_path = installer_config_data[crs_binary_key]
    
        if (not os.path.exists(crs_binary_path)):
            logging.error("Cannot find installer file " + crs_binary_path + " - will not install")
            return        
        
        field_replacements = {'INSTALL_HOME':INSTALL_DIR}
        commerce_setup_helper.substitute_file_fields(response_files_path + '/crs/crsinstaller.properties.master', response_files_path + '/crs/crsinstaller.properties', field_replacements)
        installCommand = "\"" + crs_binary_path + " -i silent -f " + response_files_path + "/crs/crsinstaller.properties" + "\"" 
        commerce_setup_helper.exec_as_user(INSTALL_OWNER, installCommand)
        
        # If patch1 is installed, these are not updated. fix it.
        cpCmd = "\"" + "cp " + INSTALL_DIR + "/DAS/taglib/dspjspTaglib/1.0/lib/dspjspTaglib1_0.jar " + INSTALL_DIR + "/CommerceReferenceStore/Store/Storefront/j2ee-apps/Storefront/store.war/WEB-INF/lib" + "\""
        commerce_setup_helper.exec_as_user(INSTALL_OWNER, cpCmd)
        cpCmd = "\"" + "cp " + INSTALL_DIR + "/DAS/taglib/dspjspTaglib/1.0/lib/dspjspTaglib1_0.jar " + INSTALL_DIR + "/CommerceReferenceStore/Store/Storefront/j2ee-apps/Storefront/storedocroot.war/WEB-INF/lib" + "\""
        commerce_setup_helper.exec_as_user(INSTALL_OWNER, cpCmd)
        cpCmd = "\"" + "cp " + INSTALL_DIR + "/DAS/taglib/dspjspTaglib/1.0/lib/dspjspTaglib1_0.jar " + INSTALL_DIR + "/CommerceReferenceStore/Store/Fluoroscope/j2ee-apps/Fluoroscope/fluoroscope.war/WEB-INF/lib" + "\""
        commerce_setup_helper.exec_as_user(INSTALL_OWNER, cpCmd)
        cpCmd = "\"" + "cp " + INSTALL_DIR + "/DAS/taglib/dspjspTaglib/1.0/lib/dspjspTaglib1_0.jar " + INSTALL_DIR + "/CommerceReferenceStore/Store/DCS-CSR/j2ee-apps/DCS-CSR/CSRHelper.war/WEB-INF/lib" + "\""
        commerce_setup_helper.exec_as_user(INSTALL_OWNER, cpCmd)
        cpCmd = "\"" + "cp " + INSTALL_DIR + "/DAS/taglib/dspjspTaglib/1.0/lib/dspjspTaglib1_0.jar " + INSTALL_DIR + "/CommerceReferenceStore/Store/EStore/Versioned/j2ee-apps/Versioned/store-merchandising.war/WEB-INF/lib" + "\""
        commerce_setup_helper.exec_as_user(INSTALL_OWNER, cpCmd)  
        
    if (INSTALL_SERVICE == "true"):
        
        logging.info("installing Service")

        service_binary_path = installer_config_data[service_binary_key]
    
        if (not os.path.exists(service_binary_path)):
            logging.error("Cannot find installer file " + service_binary_path + " - will not install")
            return           
        
        field_replacements = {'INSTALL_HOME':INSTALL_DIR}
        commerce_setup_helper.substitute_file_fields(response_files_path + '/service/serviceinstaller.properties.master', response_files_path + '/service/serviceinstaller.properties', field_replacements)
        installCommand = "\"" + service_binary_path + " -i silent -f " + response_files_path + "/service/serviceinstaller.properties" + "\"" 
        commerce_setup_helper.exec_as_user(INSTALL_OWNER, installCommand)               
