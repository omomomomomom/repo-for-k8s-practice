
---

# 🔀 Multiple Schedulers in Kubernetes (DevOps Interview Notes)

### 🧠 1. Concept (Aasan Bhasha Mein)

Soch ki teri company mein ek **Default HR (Default Scheduler)** hai, jiska kaam hai naye employees (Pods) ko unki skills ke hisaab se alag-alag departments (Nodes) mein bhejna. Uska ek set rule hai.

Par teri company mein ek **Special Secret Agent** ki team ban rahi hai. Uske liye tujhe ek alag **Special HR (Custom Scheduler)** chahiye jiske hiring rules ekdum alag aur strict hain.

Kubernetes itna flexible hai ki tu ek hi cluster mein ek sath 2, 3 ya usse zyada Schedulers chala sakta hai. Normal pods default scheduler ke paas jayenge, aur tere special pods tere custom scheduler ke paas!

---

### 🎯 2. The "Why" (Technical Reason & Use Cases)

**Default Scheduler se kaam kyu nahi chalta?**
Default scheduler mein hum Taints, Tolerations, aur Node Affinity use karke pods ko place karte hain. Par maan le tera koi ajeeb sa use-case hai:

* *"Mujhe pod tabhi is node pe dalna hai jab is node ki hard-drive ka temperature 40 degree se kam ho."*
* *"Mujhe pod schedule karne se pehle apni company ke ek external database se API call karke permission leni hai."*

Aise custom logic default scheduler mein nahi hote. Iske liye tu GO language mein apna khud ka Custom Scheduler code karta hai, use Docker image mein pack karta hai, aur cluster mein as a second scheduler deploy kar deta hai.

---

### 💻 3. Practical Example & Code Breakdown

Ek custom scheduler lagane ke 2 main steps hote hain:

#### Step 1: Scheduler ka Config File (usko naam dena)

Custom scheduler ko ek alag pehchaan deni padti hai taaki K8s confuse na ho. Ye hum uske config file mein batate hain:

```yaml
apiVersion: kubescheduler.config.k8s.io/v1
kind: KubeSchedulerConfiguration
profiles:
  - schedulerName: my-custom-scheduler   # <--- Ye naam sabse important hai!
leaderElection:
  leaderElect: false                     # <--- (Explained in Interview Q&A below)

```

*(Is config ko hum ConfigMap ke through apne custom scheduler ke Pod/Deployment mein mount karte hain).*

#### Step 2: Pod ko batana ki "Tera HR kaun hai?"

Jab tu apna application pod banayega, to tujhe explicitly batana padega ki default scheduler ko use mat karna.

**File: `my-special-pod.yaml**`

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: special-app
spec:
  schedulerName: my-custom-scheduler     # <--- Yahan humne Custom Scheduler ka naam de diya
  containers:
  - name: my-app
    image: nginx

```

---

### 🔥 4. DevOps Interview Q&A (Interviewer's Trap)

**Q1: I deployed a Pod with a custom `schedulerName`, but the Pod is stuck in the `Pending` state. What could be the issue?**

* **The Perfect Answer:** "There are usually two reasons. First, the custom scheduler pod itself might not be running or is crashing. Second, there might be a typo in the `schedulerName` inside the pod spec. If K8s cannot find an active scheduler with that exact name, the pod will remain in the `Pending` state indefinitely because no one is there to pick it up."

**Q2: How do you verify which scheduler actually placed the pod on a node?**

* **The Perfect Answer:** "We can check the Kubernetes events. By running `kubectl get events -o wide`, we can look for the 'Scheduled' event. The `SOURCE` column will clearly show the name of the scheduler (e.g., `my-custom-scheduler` instead of `default-scheduler`) that made the placement decision."

**Q3: In the Scheduler configuration, there is an option called `leaderElect`. Why is this used?**

* **The Perfect Answer:** "This is crucial for High Availability (HA). If we run 3 master nodes, we will have 3 copies of our custom scheduler running. If all 3 try to schedule the same pod at the same time, it creates a conflict. `leaderElect: true` ensures that they vote and elect only ONE active leader to do the scheduling, while the other two remain on standby. If the leader dies, a new one takes over."

---
