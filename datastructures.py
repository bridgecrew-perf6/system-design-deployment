from argparse import Action
import time

import requests
from collections import *
class DeploymentNode:
    def __init__(self, changeNumber: str, manifestName: str, action: str, project: str) -> None:
        self.children : List['DeploymentNode'] = []
        self.changeNumber = changeNumber
        self.manifestName = manifestName
        self.action = action
        self.project=project
        self.success = True
        self.done = False

    def addNextStep(self, step: 'DeploymentNode') -> None:
        self.children.append(step)

    def createSnowChange(self)-> bool:
        '''Do a curl request to ServiceNow to create change'''
        payload = {
            "manifest": "",
            "affectedCi": ""
        }
        r = requests.get('https://www.servicenow.com/create', auth=('user', 'pass'), data=payload)

        self.changeNumber = r.json()["changeNumber"]
        return self.changeNumber

    def triggerDeploy(self)-> bool:
        '''Do a curl to trigger deploy, wait for done.'''

        payload = {
            "changeNumber": self.changeNumber
        }
        r = requests.get('https://www.servicenow.com/trigger', auth=('user', 'pass'), data=payload)
    
    def checkDeploy(self):
        payload = {
            "changeNumber": self.changeNumber
        }
        r = requests.get('https://www.servicenow.com/status', auth=('user', 'pass'), data=payload)
        if r.json()['status'] == "Failed":
            self.success= False
            self.done = True
        elif r.json()['status'] == "Success":
            self.done = True
            self.success = True
        else: 
            return # in progres

class DeploymentTree:
    def __init__(self):
        self.apps = []
        self.done = []

    def addDeployment(self, node)-> None:
        self.apps.append(node)

    def deploy(self)-> bool:
        for i in self.apps:
            i.deployBfs()

    def deployBfs(self, node: 'DeploymentNode')-> bool:
        '''Trigger deploy for a single tree. Wait for completion, or fail if one of them fail.
        When it fail, will require manual intervention.'''
        layer = []
        layer.append(node)
        while len(layer) != 0:
            for child in self.children:
                child.triggerDeploy()

            success = True
            done = []
            while len(done) != len(layer):
                time.sleep(300)
                for i in len(layer):
                    child = layer[i]
                    if child.done:
                        success &= child.success
                        if not success: return 1
                        done.append(child)
            
            for i in done:
                layer.extend(i.children)

                

            
                
                    