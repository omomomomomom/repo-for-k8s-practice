
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
