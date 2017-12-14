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

import ConfigParser
import fileinput
import json
import os
import platform
import shutil
from subprocess import Popen, PIPE, STDOUT
import urllib2
import logging

logger = logging.getLogger(__name__)

def load_json_from_url(jsonUrl, key):
    """
    Read json data from a URL
    """      
    try:
        data = urllib2.urlopen(jsonUrl)
    except urllib2.URLError, e:
        logger.error("url error")
    jsonData = json.load(data)
    if key not in jsonData:
        raise ValueError ("Root " + key + " item missing")   
    return jsonData[key]

def load_json_from_file(jsonFile, key):
    """
    Read json data from a file on the filesystem
    """        
    with open(jsonFile) as data_file:    
        data = json.load(data_file)
        if key not in data:
            raise ValueError ("Root " + key + " item missing")   
        return data[key]
       
def check_required_fields(jsonData, requiredFields):
    """
    check for all requiredFields in jsonData
    """     
    for field in requiredFields:
        if field not in jsonData:
            raise ValueError ("Required field " + field + " missing from json")
 

def callPopen(command):
    """
    call external process
    """       
    proc = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)

    out, err = proc.communicate()
    if out:
        logger.info(out)
    if err:
        logger.error(err)  
    
    return proc.returncode

def substitute_file_fields_inplace(infile, replacement_dict):
    """
    Read infile. Replace any string occurrences in replacement_dict. Write result back to infile
    """      
    indata = open(infile).read()
    outdata = open(infile, 'w')
    if replacement_dict is not None:
        for i in replacement_dict.keys():
            indata = indata.replace(i, replacement_dict[i])
    outdata.write(indata)
    outdata.close 
    
            
def substitute_file_fields(infile, outfile, replacement_dict):
    """
    Read infile. Replace any string occurrences in replacement_dict. Write result to outfile
    """      
    indata = open(infile).read()
    outdata = open(outfile, 'w')
    if replacement_dict is not None:
        for i in replacement_dict.keys():
            indata = indata.replace(i, replacement_dict[i])
    outdata.write(indata)
    outdata.close 
    
def change_file_owner(file_name, user, group):
    """
    Change file owner and group
    """         
    command = "chown " + user + ":" + group + " " + file_name
    callPopen(command)  

    
def mkdir_with_perms(path, owner, group):
    """
    Make recursive directories, setting ownership along the way
    """
    # check if the entire path already exists
    if (os.path.exists(path)):
        # take ownership
        change_file_owner(path, owner, group)
    else:    
        path = path[1:]
        dirs = path.split("/")
        dirToMake = ''
        for mydir in dirs:
            dirToMake += '/' + mydir
            if not (os.path.exists(dirToMake)):
                mk_cmd = "mkdir " + dirToMake
                callPopen(mk_cmd) 
                change_file_owner(dirToMake, owner, group)

def add_to_bashrc(user, text):
    """
    Add text to a users .bashrc file
    """        
    homeDir = os.path.expanduser("~" + user)
    bashrc_file = homeDir + "/.bashrc"
    with open(bashrc_file, "a") as myfile:
        myfile.write(text)
    myfile.close()

def exec_cmd (command): 
    """
    Exec command as the user who called this function
    """        
    logger.info("exec_cmd is " + command)
    returncode = callPopen(command)
    return returncode

        
def exec_as_user (user, command):
    """
    Exec a command as another user
    """        
    COMMAND_PREFIX = "su - " + user + " -c "
    exec_cmd = COMMAND_PREFIX + command
    logger.info("exec_as_user cmd is " + exec_cmd)
    returncode = callPopen(exec_cmd)
    return returncode
            
def copy_start_script (startOnBoot, srcFile, field_replacement, dstFile=None):
    """
    Copy init scripts to /etc/init.d, and link to run on boot if startOnBoot true
    """        
    outDir = "/etc/init.d"
    path, filename = os.path.split(srcFile)
    if dstFile is None:
        outFilename = filename.replace('.master', '')
    else:
        outFilename = dstFile
        
    outFile = outDir + "/" + outFilename
    substitute_file_fields(srcFile, outFile, field_replacement)
    os.chmod(outFile, 0755)
    if (startOnBoot == 'true'):
        # solaris does not use chkconfig. add to rc dirs manually
        if (platform.system() == 'SunOS'):
            startLinkCommand = "ln -s " + outFile + " /etc/rc3.d/S99" + outFilename   
            stopLinkCommand = "ln -s " + outFile + " /etc/rc2.d/K74" + outFilename
            exec_cmd(startLinkCommand)
            exec_cmd(stopLinkCommand)
        else:
            chkCmd = "chkconfig --add " + outFilename
            exec_cmd(chkCmd)            

def copy_start_script_home (user, group, srcFile, field_replacement):
    """
    Copy init scripts to users bin directory
    """        
    homeDir = os.path.expanduser("~" + user)
    binDir = homeDir + "/bin"
    if not (os.path.exists(binDir)):
        os.mkdir(binDir, 0755)
        change_file_owner(binDir, user, group)
    path, filename = os.path.split(srcFile)
    outFile = binDir + "/" + filename.replace('.master', '')
    substitute_file_fields(srcFile, outFile, field_replacement)
    os.chmod(outFile, 0755)
    change_file_owner(outFile, user, group)
    
def copy_sshkeys(fromUser, toUser, toUserGroup):
    """
    Sync up ssh authorized_keys from one user to another
    """      
    fromHomeDir = os.path.expanduser("~" + fromUser) + "/.ssh"
    toHomeDir = os.path.expanduser("~" + toUser) + "/.ssh"
    if not (os.path.exists(toHomeDir)):
        os.mkdir(toHomeDir, 0700)
    shutil.copyfile(fromHomeDir + "/authorized_keys" , toHomeDir + "/authorized_keys")
    os.chmod(toHomeDir + "/authorized_keys", 0644)
    change_file_owner(toHomeDir + "/authorized_keys", toUser, toUserGroup)
    
def get_path_to_binary(service_name, binary_key, installer_properties):
    """
    Get the path to a product binary from properties file
    """      
    config = ConfigParser.ConfigParser()
    config.read(installer_properties)
    logging.info("config file is " + installer_properties)
    config.read(installer_properties)
    try:            
        binary_path = config.get(service_name, binary_key)
    except ConfigParser.NoSectionError:
        logging.error("Config section " + service_name + " not found in config file.")
        return False
        
    return binary_path

def get_json_key(config_data, json_key):
    """
    Return all data under a specific json key
    """       
    if json_key in config_data:
        jsonData = config_data[json_key]
    else:
        logging.error(json_key + " json key not found.")
        return False
    return jsonData

def get_installer_config_data(configData, full_path, service_name):
    """
    Get the config data on an installer
    """
    installer_data_key = 'installer_data'
    install_properties_key = 'installer_properties'
    install_versions_key = 'install_versions'
    
    # check if there is installer version data in our json
    if installer_data_key in configData:
        installer_prop_data = configData[installer_data_key]
    else:
        logging.error("installer json data missing. Cannot continue")
        return False
    
    # set the specific version of a service we are looking for
    install_versions = configData[install_versions_key]   
    install_version = install_versions[service_name]
    service_version = service_name + "_" + install_version      

    # try to load the install property file
    config = ConfigParser.ConfigParser()
    installer_props = installer_prop_data[install_properties_key]
    config_file = full_path + '/' + installer_props

    if (not os.path.exists(config_file)):
        logging.error("Installer config " + config_file + " not found. Halting")
        return False

    logging.info("Reading installer properties file " + config_file)
    config.read(config_file)
    
  
    try:            
        service_version_data = config._sections[service_version]
        service_version_data['service_version'] = service_version
    except ConfigParser.NoSectionError:
        logging.error("Config section " + service_version + " not found in config file.")
        return False
        
    return service_version_data
    
