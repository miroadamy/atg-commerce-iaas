#!/usr/bin/python

# The MIT License (MIT)
#
# Copyright (c) 2017 Oracle
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
__copyright__ = "Copyright (c) 2017 Oracle"
__version__ = "1.0.0.0"
__date__ = "@BUILDDATE@"
__status__ = "Development"
__module__ = "add_agent"
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#


import getopt
import logging
import sys

# Import utility methods
from bcc_utils import callRESTApi
from bcc_utils import clearHTTPSession

# Define methods

def addAgent(endpoint, agentDisplayName, agentDescription, excludeAssetDestinations, includeAssetDestinations, delimitedDestinationMap, agentEssential, transportURL, targetID, cookie):
    clearHTTPSession()
    data = {"agentDisplayName": agentDisplayName, "agentDescription": agentDescription, "excludeAssetDestinations": excludeAssetDestinations, 
            "includeAssetDestinations": includeAssetDestinations, "delimitedDestinationMap": delimitedDestinationMap, "agentEssential": agentEssential,
            "transportURL": transportURL, "targetID": targetID}
    basepath = '/rest/model/com/oracle/ateam/bcctools/BCCActor'
    resourcename = 'addAgent'
    params = None
    
    response = callRESTApi(endpoint, basepath, resourcename, data, 'POST', params, cookie)

    return response


# Read Module Arguments
def readModuleArgs(opts, args):
    moduleArgs = {}
    moduleArgs['endpoint'] = None
    moduleArgs['agentDisplayName'] = None
    moduleArgs['agentDescription'] = None
    moduleArgs['excludeAssetDestinations'] = ''
    moduleArgs['includeAssetDestinations'] = ''
    moduleArgs['delimitedDestinationMap'] = ''
    moduleArgs['agentEssential'] = False
    moduleArgs['transportURL'] = None
    moduleArgs['targetID'] = None
    moduleArgs['cookie'] = None

    # Read Module Command Line Arguments.
    for opt, arg in opts:
        if opt in ("-e", "--endpoint"):
            moduleArgs['endpoint'] = arg
        elif opt in ("-d", "--agentDisplayName"):
            moduleArgs['agentDisplayName'] = arg
        elif opt in ("-D", "--agentDescription"):
            moduleArgs['agentDescription'] = arg
        elif opt in ("-E", "--excludeAssetDestinations"):
            moduleArgs['excludeAssetDestinations'] = arg
        elif opt in ("-I", "--includeAssetDestinations"):
            moduleArgs['includeAssetDestinations'] = arg
        elif opt in ("-M", "--delimitedDestinationMap"):
            moduleArgs['delimitedDestinationMap'] = arg
        elif opt in ("-r", "--agentEssential"):
            moduleArgs['agentEssential'] = arg 
        elif opt in ("-t", "--transportURL"):
            moduleArgs['transportURL'] = arg 
        elif opt in ("-i", "--targetID"):
            moduleArgs['targetID'] = arg                                                                         
        elif opt in ("-C", "--cookie"):
            moduleArgs['cookie'] = arg            
    return moduleArgs


# Main processing function
def main(argv):
    # Configure Parameters and Options
    options = 'e:d:D:E:I:M:r:t:i:C:'
    longOptions = ['endpoint=', 'agentDisplayName=', 'agentDescription=', 'excludeAssetDestinations=', 'includeAssetDestinations=', 
                   'delimitedDestinationMap=', 'agentEssential=', 'transportURL=', 'targetID=', 'cookie=']
    # Get Options & Arguments
    try:
        opts, args = getopt.getopt(argv, options, longOptions)
        # Read Module Arguments
        moduleArgs = readModuleArgs(opts, args)

        if moduleArgs['endpoint'] is not None:
            response = addAgent(moduleArgs['endpoint'], moduleArgs['agentDisplayName'], moduleArgs['agentDescription'], moduleArgs['excludeAssetDestinations'], 
                                 moduleArgs['includeAssetDestinations'], moduleArgs['delimitedDestinationMap'], moduleArgs['agentEssential'], 
                                 moduleArgs['transportURL'], moduleArgs['targetID'], moduleArgs['cookie'])
            print response.text
        else:
            print ('Incorrect parameters')
    except Exception as e:
        print('Unknown Exception please check log file')
        logging.exception(e)
        sys.exit(1)

    return


# Main function to kick off processing
if __name__ == "__main__":
    main(sys.argv[1:])
