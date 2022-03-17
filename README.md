

## UML diagrams

You can render UML diagrams using [Mermaid](https://mermaidjs.github.io/). For example, this will produce a sequence diagram:

```mermaid
sequenceDiagram
Alice ->> Bob: Hello Bob, how are you?
Bob-->>John: How about you John?
Bob--x Alice: I am good thanks!
Bob-x John: I am good thanks!
Note right of John: Bob thinks a long<br/>long time, so long<br/>that the text does<br/>not fit on a row.

Bob-->Alice: Checking with John...
Alice->John: Yes... John, how are you?
```

# system-design-deployment-tree
Organize deployment tree and store it locally so the business people can visualize it.

# The gist:
- The deployment order for each app looks like a B-tree - can be serialized - https://leetcode.com/problems/serialize-and-deserialize-n-ary-tree/
- The deployment order for the whole platform is an ordered forest - think of an array/json

# Data example:
```json
["UninstallArtifact1,InstallArtifact2)UninstallArtifact3,InstallArtifact3))",
"UninstallArtifact1,UninstallArtifact3)InstallArtifact4)InstallArtifact2)"]
```

![App2](tree1.JPG)
![App3](tree2.JPG)

### Deploy/Rollback Planning Flow
```mermaid
sequenceDiagram
	participant User
	participant Frontend
	participant Backend
	participant Storage
	participant ServiceNow

	User ->> Frontend: add packages, actions and orders to deploy
	Frontend ->> Backend: serialize the tree and send to backend
	Backend ->> ServiceNow: deserialize then create CHG number
	Backend ->> Storage: save deployment
	ServiceNow -->> Backend: CHG number
	Backend -->> Frontend: send deployment tree with CHG
	Backend -->> Storage: Serialize then store packages, action, order and change number
	Frontend -->> User: present to user
```
### Deploy/Rollback Apply Flow
```mermaid
sequenceDiagram
	participant User
	participant Frontend
	participant Backend
	participant Storage
	participant ServiceNow
	participant NotificationService

	User ->> Frontend: Choose a deployment tree with CHG to run
	Frontend ->> Backend: Serialize the tree and send to backend
	Backend -) ServiceNow: deserialize then trigger the CHG layer by layer (breadth-first search traversal)
	loop Check status once very few minutes
		Backend ->> ServiceNow: check for deployment/rollback status
		ServiceNow->> Backend : response status
		opt Success 
			Backend ->> Storage: Save status, mark as done and continue with next CHG action, or wait for the layer to finish
			Backend -) NotificationService: notify subscriber
		end
		opt Fail
			Backend ->> Storage: Save status, exit
			Backend -) NotificationService: notify subscriber
		end		
	end
```
### Checking Deployment Status
```mermaid
sequenceDiagram
	participant User
	participant Frontend
	participant Backend
	participant Storage
	participant ServiceNow
	loop Check status once in a while
	User ->> Frontend: request deployment status
	Frontend ->> Backend: Send deployment ID
		Backend ->> Storage: Request serialized data
		Storage->> Backend : Send serialized data
		Backend -->> Frontend: send deployment tree with CHG and status
		Frontend -->> User: present to user
	end
```

![System design](system.jpg)

## Improvements:
- Convert/export to JSON option.

