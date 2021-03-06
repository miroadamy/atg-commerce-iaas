#!/usr/bin/python
# Copyright (c) 2013, 2014-2017 Oracle and/or its affiliates. All rights reserved.

DOCUMENTATION = '''
---
module: oc_machineimage
short_description: Short Desc
description:
    - Long Desc
version_added: ""
options:
    action:
        description:
            - Action to be executed against the oracle cloud object
        required: false
        default: list
        choices: ['create', 'list', 'update', 'delete']
    endpoint:
        description:
            - Oracle Cloud Endpoint
        required: true
        default: null
    user:
        description:
            - Oracle cloud user only required is cookie is not present.
        required: false
        default: null
    password:
        description:
            - Oracle cloud password only required is cookie is not present.
        required: false
        default: null
    cookie:
        description:
            - Oracle cloud authentication cookie.
        required: false
        default: null
    resourcename:
        description:
            - Resource name associated with object we are working with.
        required: false
        default: null
requirements: [oraclecloud]
author: "Andrew Hopkinson (Oracle Cloud Solutions A-Team)"
notes:
    - Simple notes
...
'''

EXAMPLES = '''
'''

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
__author__ = "Andrew Hopkinson (Oracle Cloud Solutions A-Team)"
__copyright__ = "Copyright (c) 2013, 2014-2017 Oracle and/or its affiliates. All rights reserved."
__ekitversion__ = "@VERSION@"
__ekitrelease__ = "@RELEASE@"
__version__ = "1.0.0.0"
__date__ = "@BUILDDATE@"
__status__ = "Development"
__module__ = "oc_machineimage"
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

import os
import sys

from oc.oc_exceptions import REST401Exception
from oc.oc_exceptions import OCActionNotPermitted
from oc.oc_exceptions import REST409Exception
from oc.oc_exceptions import OCObjectAlreadyExists
from oc.oc_exceptions import OCObjectDoesNotExist

from oc.create_machine_image import createMachineImage
from oc.list_machine_images import listMachnineImages
from oc.delete_machine_image import deleteMachineImage

# Main processing function
def main():
    module = AnsibleModule(
            argument_spec = dict(
                    action          = dict(default='list', choices=['create', 'list', 'delete']),
                    endpoint        = dict(required=True, type='str'),
                    user            = dict(required=False, type='str'),
                    password        = dict(required=False, type='str'),
                    cookie          = dict(required=False, type='str'),
                    resourcename    = dict(required=True, type='str'),
                    name            = dict(required=False, type='str'),
                    fileurl         = dict(required=False, type='str'),
                    account         = dict(required=False, type='str'),
                    noupload        = dict(required=False, type='bool', default=True)
            )
    )

    endpoint = module.params['endpoint']
    user = module.params['user']
    password = module.params['password']
    cookie = module.params['cookie']
    if cookie is None and user is not None and password is not None:
        cookie = authenticate(endpoint, user, password)
    resourcename = module.params['resourcename']
    name = module.params['name']
    fileurl = module.params['fileurl']
    account = module.params['account']
    noupload = module.params['noupload']

    changed = True
    jsonobj = module.params

    try:
        if module.params['action'] == 'create':
            jsonobj = createMachineImage(endpoint, resourcename, cookie, name, fileurl, account, noupload)
            module.exit_json(changed=True, list=jsonobj)
        elif module.params['action'] == 'list':
            jsonobj = listMachnineImages(endpoint, resourcename, cookie)
            module.exit_json(changed=True, list=jsonobj)
        elif module.params['action'] == 'delete':
            jsonobj = deleteMachineImage(endpoint, resourcename, cookie)
            module.exit_json(changed=True, list=jsonobj)
        else:
            module.fail_json(msg="Unknown action")
    except OCObjectAlreadyExists as e:
        module.exit_json(changed=False, list=jsonobj)
    except OCObjectDoesNotExist as e:
        module.exit_json(changed=False, list=jsonobj)
    except Exception as e:
        module.fail_json(msg=str(e.message))

    return


# import module snippets
from ansible.module_utils.basic import *
from ansible.module_utils.splitter import *

# Main function to kick off processing
if __name__ == "__main__":
    main()
