
---

# 👻 Kubernetes DaemonSets (DevOps Interview Notes)

### 🧠 1. Concept (Aasan Bhasha Mein)

Soch ki teri ek badi building (Cluster) hai jisme bohot saare gates (Nodes) hain.

* Agar tu **Deployment** use karta hai, to tu bolta hai: *"Mujhe 5 security guards chahiye."* Wo guards kisi bhi gate pe khade ho sakte hain.
* Par agar tu **DaemonSet** use karta hai, to tu bolta hai: *"Mujhe **HAR EK GATE** pe exactly ek security guard chahiye."*

**DaemonSet ka simple funda:** Ye make sure karta hai ki tere cluster ke **har ek Worker Node** par tere Pod ki exactly **Ek Copy (Instance)** hamesha chal rahi ho.

Agar kal ko auto-scaling ki wajah se ek naya Node add hota hai, to DaemonSet automatically us naye node par ek Pod daal dega. Aur agar node delete hota hai, to pod bhi uske sath chala jayega. Tujhe manual scaling karne ki koi zarurat nahi!

---

### 🎯 2. The "Why" (Technical Reason & Use Cases)

**Bina DaemonSet ke kya problem aati?**
Agar tu standard `ReplicaSet` ya `Deployment` se monitoring set karta, to tujhe manually track karna padta ki kitne nodes hain aur utne hi replicas set karne padte. Naya node aane par fir se scaling command chalani padti. DaemonSet is manual headache ko khatam kar deta hai.

**Real-World DevOps Use Cases (Industry Standard):**

1. **Monitoring Agents:** Cluster ke har node ka CPU/RAM data nikalne ke liye. (e.g., **Prometheus Node Exporter**, Datadog agent).
2. **Log Collection:** Har node se application logs collect karke central server pe bhejne ke liye. (e.g., Fluentd, Logstash).
3. **Networking & Security:** Cluster ke andar pods ki networking manage karne ke liye. (e.g., Calico agent, WeaveNet, `kube-proxy`).

---

### 💻 3. Practical Example & Code Breakdown

DaemonSet ka YAML bilkul `Deployment` jaisa dikhta hai, bas ek bada difference hota hai: **Isme `replicas` field nahi hota!** (Kyunki replicas to nodes ke count pe depend karte hain).

**File: `monitoring-daemon.yaml**`

```yaml
apiVersion: apps/v1
kind: DaemonSet          # <--- (Kind change ho gaya)
metadata:
  name: fluentd-elasticsearch
  labels:
    k8s-app: fluentd-logging
spec:
  selector:
    matchLabels:
      name: fluentd-elasticsearch
  template:              # <--- (Yahan se Pod ki definition shuru)
    metadata:
      labels:
        name: fluentd-elasticsearch
    spec:
      containers:
      - name: fluentd-elasticsearch
        image: fluentd:latest

```

**Cheat Codes (Commands):**

* Create karna: `kubectl apply -f monitoring-daemon.yaml`
* List dekhna: `kubectl get daemonsets` (ya shortcut: `kubectl get ds`)
* Detail mein dekhna: `kubectl describe ds fluentd-elasticsearch`

---

### 🔥 4. DevOps Interview Q&A (Interviewer's Trap)

**Q1: What is the exact difference between a Deployment and a DaemonSet?**

* **The Perfect Answer:** "Sir, a Deployment ensures that a specific *number of replicas* are running across the cluster, regardless of which node they land on. A DaemonSet ensures that exactly *one copy of a Pod* runs on *every single node* (or a selected subset of nodes) in the cluster."

**Q2: We use AWS Auto Scaling Groups (ASG) for our worker nodes. What happens to the DaemonSet when the ASG spins up a new EC2 instance?**

* **The Perfect Answer:** "As soon as the new EC2 instance joins the Kubernetes cluster as a worker node, the DaemonSet Controller detects it and automatically schedules a new DaemonSet pod onto that node. No manual intervention or scaling command is required."

**Q3: (Deep Architecture Question) How does the DaemonSet actually schedule pods on every node? Does it use the default scheduler?**

* **The Perfect Answer:** "In older versions of Kubernetes (prior to v1.12), the DaemonSet controller bypassed the default scheduler by directly setting the `nodeName` field in the Pod spec. However, from v1.12 onwards, DaemonSets use the default scheduler and automatically apply `NodeAffinity` rules to place the pods. This ensures better compatibility with other scheduling rules and preemption." *(Bhai, ye answer dega to interviewer khush ho jayega, ye actual internal architecture hai!)*

**Q4: Can I run a DaemonSet only on specific nodes? For example, I only want a monitoring agent on my GPU nodes, not CPU nodes.**

* **The Perfect Answer:** "Yes, absolutely! While DaemonSets run on all nodes by default, we can restrict them using `nodeSelector` or `nodeAffinity` inside the DaemonSet's pod template spec. It will then ensure one pod runs *only* on the nodes that match those labels."

*** Bhai, ye notes tere GitHub ke liye ekdum ready hain. Ek baar padhega to pura concept clear rahega. Next transcript ready rakh, isko foddte hain! 🚀


*** extra point to node ***

---

### 🛠️ Creating DaemonSet Imperatively (The Exam/Interview Trick)

**Concept:** Kubernetes CLI (`kubectl`) mein DaemonSet ke liye direct `create` command exist nahi karti. Exam (CKA) ya Interview tasks mein time bachane ke liye hum **Deployment** ki command use karke uska structure (YAML) generate karte hain aur usme minor edits karte hain. Isse scratch se file likhne ka time bachta hai.

**Steps to Create:**

1. **Generate Skeleton (Deployment ka YAML churao):**
Sabse pehle Deployment ki command use karke YAML file generate karo bina resource create kiye (`--dry-run`):
```bash
kubectl create deployment my-ds --image=nginx --dry-run=client -o yaml > ds.yaml

```


2. **Edit the File (`vi ds.yaml`):**
File kholo aur bas ye 3 changes karo:
* **Change Kind:** `Kind: Deployment` ➝ `Kind: DaemonSet`
* **Remove Replicas:** `replicas: 1` wali line delete kar do (Kyunki DS har node pe chalta hai, count fix nahi hota).
* **Remove Strategy:** `strategy: {}` wali line delete kar do.


3. **Apply the File:**
```bash
kubectl apply -f ds.yaml

```



---