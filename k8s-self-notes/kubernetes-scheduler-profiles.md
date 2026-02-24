
---

# ⚙️ Kubernetes Scheduler Profiles & Framework (Advanced)

### 🧠 1. The Scheduling Journey (Ek Pod Node tak kaise pohochta hai?)

Jab tu ek Pod banata hai, to wo seedha node pe nahi girta. Wo ek lambe process (Pipeline) se guzarta hai. Is process ke 4 main stages hote hain:

1. **Scheduling Queue (Line mein lagna):** Pods queue mein lagte hain. Yahan **PriorityClass** dekhi jati hai. Jiska priority VIP hai, wo line mein aage chala jata hai.
2. **Filter Phase (Rejection):** K8s dekhta hai ki kis node ke paas resources (CPU/RAM) nahi hain. Jinke paas nahi hai, unhe list se hata diya jata hai. (e.g., Taints, NodeSelector check hote hain).
3. **Scoring Phase (Marks dena):** Jo nodes bach gaye, unko 0-100 tak marks milte hain. Agar kisi node pe Pod ki Image pehle se downloaded hai, to usko extra marks milte hain! Jiske sabse zyada marks, wo node jeet gaya.
4. **Binding Phase (Rishta pakka):** Pod ko us winning node ke sath bind (attach) kar diya jata hai.

---

### 🧩 2. Extension Points & Plugins (The Customization)

Kubernetes ne is pure process ko "Extensible" banaya hai. Har stage (Queue, Filter, Score, Bind) pe ek **"Extension Point"** (socket) hota hai jahan tu alag-alag **"Plugins"** laga sakta hai.

* *QueueSort Plugin:* Queue ko sort karta hai.
* *NodeResourcesFit Plugin:* Filter aur Score dono phases mein kaam karta hai CPU/RAM check karne ke liye.
* *ImageLocality Plugin:* Scoring phase mein kaam karta hai.

Agar tujhe K8s ka default logic pasand nahi, to tu C++ ya GO mein apna code likh ke in points pe plug kar sakta hai!

---

### 🎯 3. The Problem: Multiple Schedulers vs. The Solution: Profiles

Pichle lecture mein humne 3 alag-alag Custom Schedulers banaye thhe (3 alag pods/binaries).

**The Core Problem (Race Condition):** Agar 3 alag-alag Schedulers ek sath chal rahe hain, to unhe ek dusre ka nahi pata. Soch, Node-1 pe sirf 2GB RAM bachi hai.

* *Scheduler A* ne socha "Main yahan pod dalunga."
* *Scheduler B* ne bhi usi time socha "Main bhi yahan pod dalunga."
Dono ne ek sath pod bhej diye aur Node crash ho gaya! Isko **Race Condition** bolte hain.

**The Ultimate Solution (Scheduler Profiles - v1.18+):**
Ab hum 3 alag binary/pods nahi chalate. Hum **EK HI Scheduler** (Single Binary) chalate hain, par uske andar **Multiple Profiles (Personalities)** bana dete hain. Kyunki brain ek hi hai, usko pata hota hai ki total resources kitne bache hain, to koi fight (Race condition) nahi hoti!

---

### 💻 4. Practical Example & Code Breakdown

Hum Scheduler ki config file mein `profiles` list banate hain. Har profile mein hum specific plugins ko On/Off (enable/disable) kar sakte hain.

**File: `multi-profile-config.yaml**`

```yaml
apiVersion: kubescheduler.config.k8s.io/v1
kind: KubeSchedulerConfiguration
profiles:
  # PROFILE 1: Ye humara Default jaisa kaam karega
  - schedulerName: default-scheduler

  # PROFILE 2: Custom jisme Taints/Tolerations ka rule hata diya hai
  - schedulerName: my-no-taint-scheduler
    plugins:
      filter:               # <--- Filter phase mein modification
        disabled:
          - name: TaintToleration  # <--- Is plugin ko band kar diya!

  # PROFILE 3: Custom jisme Scoring hoti hi nahi (Fast placement)
  - schedulerName: my-fast-scheduler
    plugins:
      score:                # <--- Score phase mein modification
        disabled:
          - name: '*'       # <--- Star (*) matlab saare scoring plugins band!

```

*Ab tu pod banate waqt `schedulerName: my-no-taint-scheduler` likhega, to K8s ek hi engine ke andar us specific logic/profile se tera pod schedule karega!*

---

### 🔥 5. DevOps Interview Q&A (Interviewer's Trap)

**Q1: What are the four main phases of Pod scheduling in Kubernetes?**

* **The Perfect Answer:** "The scheduling process goes through four main phases: **Queueing** (sorting pods by priority), **Filtering** (eliminating nodes that don't meet requirements), **Scoring** (ranking the remaining nodes), and finally **Binding** (assigning the pod to the node with the highest score)."

**Q2: We want to run custom scheduling logic. Why is it recommended to use 'Scheduler Profiles' instead of deploying a completely separate Scheduler binary?**

* **The Perfect Answer (Trap Alert 🚨):** "If we run multiple independent scheduler binaries, they are unaware of each other's decisions. This can lead to **Race Conditions** where multiple schedulers try to schedule different pods onto the same node resources simultaneously. By using **Scheduler Profiles** within a single scheduler binary, the single process maintains a centralized view of the cluster state, completely avoiding race conditions while still providing custom scheduling logic."

**Q3: Can I disable a default plugin for a specific application without affecting the rest of the cluster?**

* **The Perfect Answer:** "Yes! We can create a new Scheduler Profile in the configuration file, disable that specific plugin (for example, under the `filter` or `score` extension points), and give this profile a unique `schedulerName`. Then, we simply assign that `schedulerName` to our specific application's Pod spec. The rest of the cluster will continue using the `default-scheduler` profile."

---

###**"Real-World Scenarios of Scheduler Profiles"** 

---

# 🎭 Real-World Behavior of Scheduler Profiles

### 🏢 The Scenario (Maan lo hamare paas 3 Nodes hain):

* **Node-1:** 16GB RAM hai, par ispe ek **Taint** laga hai (`gpu=true:NoSchedule`). Yani aam pods yahan nahi aa sakte.
* **Node-2:** 8GB RAM hai, ekdum free hai (No Taints).
* **Node-3:** 2GB RAM hai, ekdum free hai (No Taints).

Ab dekhte hain ki tera YAML config in nodes pe kaise khelega. Sabse pehle, Pod ya Deployment ko profile assign kaise karte hain?

*(Deployment mein `schedulerName` hamesha `template.spec` ke andar jaata hai, bahar nahi!)*

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  template:
    spec:
      schedulerName: my-no-taint-scheduler  # <--- Yahan assign hota hai!
      containers:
      - image: nginx

```

---

### 1️⃣ PROFILE 1: `default-scheduler` (The Good Boy 😇)

* **Kise lagayenge:** Tere normal web apps, frontend, APIs.
* **Behave kaise karega:**
1. **Filter:** Ye dekhega ki Node-1 pe Taint hai. Tera pod simple hai (koi toleration nahi), to ye Node-1 ko reject (filter out) kar dega. Bacha Node-2 aur Node-3.
2. **Score:** Ye dekhega Node-2 ke paas 8GB RAM hai, aur Node-3 ke paas sirf 2GB. Ye Node-2 ko zyada marks (score) dega.
3. **Result:** Tera pod safely **Node-2** pe chala jayega.



---

### 2️⃣ PROFILE 2: `my-no-taint-scheduler` (The Rule Breaker 😈)

*(Tune config mein `TaintToleration` plugin ko `disabled` kar diya hai).*

* **Kise lagayenge:** Jab tujhe kuch admin pods, monitoring agents, ya special jobs chalani hain aur tu nahi chahta ki har ek YAML file mein baith ke 10 line ka `tolerations` block likhe.
* **Behave kaise karega:**
1. **Filter:** Ye jab Node-1 ko dekhega, to iska Taint wala chashma utra hua hoga (plugin disabled hai). Isko Node-1 ka Taint dikhega hi nahi! Isko lagega Node-1 ekdum normal hai.
2. **Score:** Teeno nodes filter pass kar lenge. Phir scoring hogi. Node-1 ke paas sabse zyada RAM (16GB) hai, to isko sabse zyada marks milenge.
3. **Result:** Tera aam pod seedha Tainted **Node-1** pe jaake baith jayega bina kisi toleration ke!


* **Kya Kar Sakte Hain/Kya Nahi:** Tu isse strict isolation rules bypass karwa sakta hai. Par iska galat use kiya to tere secure/reserved nodes pe kachra (unwanted pods) bhar jayega.

---

### 3️⃣ PROFILE 3: `my-fast-scheduler` (The Speed Demon ⚡)

*(Tune config mein `score: disabled: - name: '*'` kar diya hai, matlab Scoring hogi hi nahi).*

* **Kise lagayenge:** Maan le tere paas AI/Machine Learning ka batch job hai jo ek sath 10,000 chote-chote pods banata hai. Agar K8s har pod ke liye marks calculate karne baitha, to scheduling bohot slow ho jayegi. Wahan hume marks nahi, "Speed" chahiye.
* **Behave kaise karega:**
1. **Filter:** Ye normal filter karega (Node-1 ko reject karega Taint ki wajah se). Node-2 aur Node-3 pass ho gaye.
2. **Score:** Ye phase **SKIP** ho jayega! Ye marks calculate karega hi nahi ki kahan zyada RAM hai ya kahan image pehle se padi hai.
3. **Result:** Jo bhi node isko list mein pehle dikhega (ya randomly), ye pod ko wahan phek dega. Ho sakta hai ye 8GB wale Node-2 ko chhod ke tera pod 2GB wale Node-3 pe daal de.


* **Kya Kar Sakte Hain/Kya Nahi:** Scheduling lightning fast hogi, latency kam hogi. Par tera cluster un-optimized ho jayega (resources ka sahi use nahi hoga).

---

### 🔥 DevOps Interview Q&A (The Ultimate Test)

**Interviewer:** "We have a critical batch processing system that launches 5,000 pods per minute. The default scheduler is becoming a bottleneck because it takes too long to score nodes. How can we speed this up without entirely replacing the default scheduler for our other web apps?"

**Your Answer (The Perfect Answer):**
"Sir, we can solve this by configuring **Scheduler Profiles** within the existing `kube-scheduler` configuration. We will create a new profile (e.g., `batch-scheduler`) and inside its `plugins` configuration, we will disable all plugins for the `score` extension point using the wildcard `*`.
When our batch jobs are created, we set their `schedulerName` to `batch-scheduler`. The scheduler will only filter the nodes and completely skip the scoring phase, binding the pods extremely fast. Meanwhile, our web apps will continue using the `default-scheduler` profile, keeping their placement highly optimized."

---
