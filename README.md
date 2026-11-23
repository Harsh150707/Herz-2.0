Herz 2.0: Friend Recommendation and Connection System

A course project for Data Structures (with Discrete Mathematics graph theory). People are the vertices of a graph and friendships are the edges. Every recommendation, path, spanning tree and graph property in the app is computed by algorithms written by hand in server.py, with no graph libraries.

Author: (add your name, division and roll number)

Off Campus code: HBPBTF

What the app does
Login with a name and email.
Choose interests from 6 categories: Sports, Movies, Music, Gaming, Tech, Travel.
Discover people: search by name, see mutual friends, shared interests and how many hops away each person is, ranked by a graph-based score.
Send a friend request, and accept or decline requests you receive.
Chat once a request is accepted.
Graph Lab: run BFS, DFS, components, shortest path, Dijkstra, Kruskal, Prim, cycle detection, bipartite check, Euler check and graph coloring on the live network, and see the result highlighted on the drawn graph. It also shows the adjacency list, adjacency matrix and graph statistics.

The app starts with 20 sample people. Real users who sign up appear in the same network.

Project files
File	Role
server.py	Backend: graph data structures and algorithms, friend requests, chat, and the web server
index.html	Page skeleton
style.css	Styling (light and dark mode)
app.js	Front end: draws the screens and graph, calls the server
requirements.txt	Dependencies (none beyond Python itself)

Keep all files in the same folder.

How to run
Install Python 3.8 or newer from python.org (on Windows, tick "Add Python to PATH").
Open a terminal in the project folder (in VS Code: Terminal > New Terminal).
Start the server:
python server.py

Use py server.py or python3 server.py if python is not found. To use another port: python server.py 8080. 4. Open http://localhost:8000 in a browser. 5. Stop the server with Ctrl+C.

Do not open index.html by double-clicking it: the page needs the server running.

Using it with a friend
Same Wi-Fi: find your IPv4 address with ipconfig and have your friend open http://<your-ip>:8000. Allow the firewall prompt on private networks.
To test alone, open two different browsers (or a normal and a private window) and log in as two different people.
How the files work together
Browser (index.html + style.css + app.js)  <--- JSON over HTTP --->  server.py
         draws screens and the graph                       all graph logic and data

app.js calls the endpoints below and re-syncs every 2 seconds so new requests and messages appear.

Endpoint	Purpose
POST /api/login	Create or find a user (name, email, interests)
GET /api/state?me=ID	Users, friendships, requests and chats for one user
GET /api/recommendations?me=ID	Ranked people to connect with
POST /api/request	Send a friend request
POST /api/accept and POST /api/decline	Answer a request
POST /api/chat	Send a chat message
GET /api/graph/stats	Graph statistics, adjacency list, adjacency matrix
GET /api/graph/run?algo=..&a=..&b=..	Run one algorithm. algo is one of bfs dfs comp sp dij kru pri cyc bip eul col
Data structures used
Data structure	Where
Graph as adjacency list	Graph.adj (one ordered dict per person)
Adjacency matrix	adjacency_matrix()
Hash table / set	O(1) friend checks, seen, dist, parent, color, pending requests
Queue	deque in BFS, list queue in the bipartite check
Stack	DFS recursion and the path stack in cycle detection
Disjoint set (union-find)	DisjointSet with path compression, used by Kruskal
Trees	BFS tree and minimum spanning tree
Arrays / lists	Distance array, component array, visit orders
Sorting	Kruskal edge order, Welsh-Powell degree order, recommendation ranking
Algorithms and complexity
Feature	Algorithm	Time
Hops away, shortest path	BFS	O(V + E)
Visit order, cycle detection	DFS	O(V + E)
Connected components	BFS from each unvisited vertex	O(V + E)
Closest circle (weight = 1 + interests not shared)	Dijkstra (array scan)	O(V²)
Spanning forest	Kruskal with union-find	O(E log E)
Spanning tree	Prim (scan version)	O(V · E)
Bipartite check	BFS 2-coloring	O(V + E)
Team groups	Welsh-Powell greedy coloring	O(V²)
Euler trail or circuit	Degree parity plus component check	O(V + E)
Triangles	Common neighbors per edge	O(E · degree)
Recommendations	Mutual friends, Adamic-Adar and Jaccard score, then sort	O(V · degree + V log V)

Recommendation score: 2 × Adamic-Adar(mutual friends) + 3 × Jaccard(interests), with existing friends pushed to the bottom.

Syllabus topics covered

Graph representations (adjacency list and matrix), directed vs undirected terminology, degree and the handshake lemma, connected components, paths and cycles, Euler tours, trees, bipartite graphs and 2-coloring, planar-graph edge bound (E ≤ 3V − 6), graph coloring, BFS and DFS with applications, cycle detection, minimum spanning trees (Prim and Kruskal) and shortest paths (BFS and Dijkstra).

Customizing the sample data

Edit the lists at the top of server.py: NAMES, INTERESTS and EDGES. Keep NAMES and INTERESTS the same length (a person's ID is their position, starting at 0). Interest numbers: 0 Sports, 1 Movies, 2 Music, 3 Gaming, 4 Tech, 5 Travel. Restart the server after editing.

Limitations
Data lives in memory, so restarting the server resets all users, requests and chats.
There are no passwords: logging in again with the same email returns the same account.
Sample people (IDs below 20) accept requests and reply in chat automatically; real users do this themselves.
Dijkstra and Prim use simple scans instead of a priority queue, which could be improved with a min-heap.
