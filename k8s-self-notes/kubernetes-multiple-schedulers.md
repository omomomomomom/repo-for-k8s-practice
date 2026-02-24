
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

---

# 🔀 Multiple Schedulers in Detail (Deep Dive)

### 🧠 1. The Core Problem & Solution (Kyu chahiye naya Scheduler?)

* **Default Scheduler ka Kaam:** Kubernetes ka apna ek default scheduler hota hai jiska naam hai `default-scheduler`. Ye taints, tolerations, aur node affinity ke hisaab se pods ko nodes par bhejta hai.
* **Problem:** Maan le tera ek ajeeb sa requirement hai ki *"Pod schedule hone se pehle mere company ke external database se approval le."* Default scheduler ye nahi kar sakta.
* **Solution:** Kubernetes "Extensible" (flexible) hai. Tu apna khud ka code likh kar ek naya scheduler bana sakta hai aur use K8s mein daal sakta hai. Ab tere cluster mein **2 Schedulers** honge. Normal pods default wale ke paas jayenge, aur tere special pods tere custom scheduler ke paas.

---

### 🏗️ 2. Custom Scheduler Ko Deploy Kaise Karein? (The Confusing Part)

Transcript mein instructor ne ise deploy karne ke tareeke bataye hain. Pehle purane zamane mein hum ise as a Linux Service (binary file) chalate thhe. Par aajkal (`kubeadm` ke zariye) hum har cheez ko **Pod ya Deployment** ke form mein hi chalate hain.

Instructor ne Custom Scheduler ko as a **Deployment** chalane ka example diya. Ise chalane ke liye 3 cheezein lagti hain:

#### A. The Configuration File (Naamkaran)

K8s ko kaise pata chalega ki ye naya scheduler hai? Uske liye hum ek config file banate hain jisme uska naam likhte hain:

```yaml
apiVersion: kubescheduler.config.k8s.io/v1
kind: KubeSchedulerConfiguration
profiles:
  - schedulerName: my-custom-scheduler  # <--- Asli pehchaan

```

#### B. ConfigMap & Volume Mounts (File ko andar kaise bhejein?)

Ye sabse confusing part tha lecture ka. Dhyan se samajh:
Tera Custom Scheduler ek Pod (container) ke andar chal raha hai. Us container ko ye upar wali Config File kaise milegi?

1. **ConfigMap:** Hum is config file ke text ko K8s mein as a 'ConfigMap' save kar dete hain. (ConfigMap samjho ek digital chithi hai).
2. **Volume Mount:** Fir hum pod ki YAML mein likhte hain ki is ConfigMap (chithi) ko pakdo, aur container ke andar `/etc/kubernetes/` folder mein ek physical file banake chipka do. Is process ko Volume Mounting kehte hain. Ab container read kar lega ki uska naam `my-custom-scheduler` hai.

#### C. Authentication (RBAC / Service Accounts)

Custom Scheduler ko Kube API Server se baat karni hoti hai (pods ki details lene ke liye). Isliye hume Service Accounts aur RoleBindings banane padte hain taaki usko API access karne ka 'ID Card' mil sake. *(Instructor ne bola ise abhi ignore karo agar Security section nahi padha hai).*

---

### 👑 3. What is "Leader Election"? (Interview VVIP)

Transcript mein ek concept aaya: `leaderElect: true`. Ye kya hai?

Maan le tere production cluster mein High Availability (HA) ke liye **3 Master Nodes** hain. Tune apna Custom Scheduler as a Deployment chalaya jiske `replicas: 3` hain (taaki ek mare to baaki zinda rahein).

* **Chaos (Problem):** Ab tere paas 3 Custom Schedulers chal rahe hain. Agar ek naya special pod aata hai, to teeno schedulers usko ek sath kisi node par dalne ki koshish karenge. Kalesh ho jayega!
* **Leader Election (Solution):** Agar hum `leaderElect: true` kar dete hain, to ye teeno aapas mein voting karte hain aur ek ko **Leader (Captain)** bana dete hain. Sirf Leader hi pods ko schedule karega. Baaki do chup-chaap "Standby" (Wait) karenge. Agar leader crash hua, tabhi doosra aage aayega.
* *Note: Agar tu sirf 1 hi pod chala raha hai (replicas: 1), to tu `leaderElect: false` rakh sakta hai.*

---

### 💻 4. Using & Troubleshooting the Custom Scheduler

Ab tera scheduler chal raha hai. Ek normal Pod ko iske paas kaise bhejein?

**Step 1: Assign it in the Pod YAML**
Tujhe apne app wale pod ki file mein `schedulerName` add karna padega.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: special-app
spec:
  schedulerName: my-custom-scheduler   # <--- Ye line batati hai ki Default HR ke paas mat jao
  containers:
  - image: nginx
    name: nginx

```

**Step 2: Troubleshooting (Agar Pod Pending reh jaye)**
Agar tu pod create karta hai aur wo start nahi hota (`Pending` state mein rehta hai), iska matlab hai:

1. Tune `schedulerName` ki spelling galat likhi hai.
2. Tera custom scheduler wala pod fail ho gaya hai.
Kyunki tune explicitly default scheduler ko mana kar diya tha, ab us pod ko koi pick nahi kar raha.

**Step 3: Verification (Pata kaise karein kisne schedule kiya?)**
Instructor ne bataya ki hum events check kar sakte hain:

```bash
kubectl get events -o wide

```

Output mein ek `SOURCE` column hota hai. Agar wahan `default-scheduler` ki jagah tere `my-custom-scheduler` ka naam aa raha hai, matlab tera naya scheduler perfect kaam kar raha hai!

---

---

# 🔄 The Data Flow: Custom Scheduler (Under the Hood)

Soch ki Custom Scheduler ek **Naya Employee (Robot)** hai. Ise chalane ke liye 3 cheezein chahiye:

1. **Body/Brain:** Custom Scheduler ka Docker Image (Code).
2. **Settings (Data):** Usko kaam kaise karna hai, uska naam kya hoga (Configuration File).
3. **Delivery Mechanism:** Wo settings ki kitaab us robot ke dimaag tak kaise pahuchegi (ConfigMap + Volume).

Yahan se data ka actual flow start hota hai:

### Step 1: The Raw Data (Configuration File) 📝

Sabse pehle tere paas tere laptop pe ek normal text file hoti hai (e.g., `my-scheduler-config.yaml`). Is **actual data** mein sirf naam nahi, balki ye sab hota hai:

```yaml
apiVersion: kubescheduler.config.k8s.io/v1
kind: KubeSchedulerConfiguration
profiles:
  - schedulerName: my-custom-scheduler   # <-- Data 1: Tera Naam
leaderElection:
  leaderElect: true                      # <-- Data 2: HA Settings
  resourceNamespace: kube-system         # <-- Data 3: Lock kahan banana hai

```

* **Kahan hai ye data abhi?** Tere laptop/terminal pe as a plain text.

### Step 2: The Carrier (ConfigMap) 📦

Kubernetes seedha tere laptop se file nahi padh sakta. K8s ko apna format chahiye. To tu is plain text file ko K8s ke database (etcd) mein save karne ke liye usko ek **ConfigMap** ke dabbe mein daal deta hai.

```bash
kubectl create configmap custom-scheduler-config --from-file=my-scheduler-config.yaml -n kube-system

```

* **Kahan hai ye data abhi?** K8s ke internal database (etcd) mein safely store ho gaya hai.

### Step 3: The Delivery Boy (Volume Mounts) 🚚

Ab tu apne Custom Scheduler ka **Pod/Deployment** banata hai. Us pod ko start hote waqt wo settings chahiye. Yahan `Volume` aur `VolumeMount` ka role aata hai.

* **Volume:** Pod K8s ko bolta hai, *"Jaake us `custom-scheduler-config` naam ke dabbe (ConfigMap) se data utha la."*
* **VolumeMount:** Pod bolta hai, *"Ab is data ko mere container ke andar ek physical file bana ke `/etc/kubernetes/` folder mein rakh de."*
* **Kahan hai ye data abhi?** Container ke andar ek actual file (`/etc/kubernetes/my-scheduler-config.yaml`) ban chuki hai!

### Step 4: The Engine Starts (Command Execution) ⚙️

Pod ki YAML mein container ko start karne ki command hoti hai. Ye command us file ko read karti hai:

```yaml
containers:
- name: my-custom-scheduler
  image: k8s.gcr.io/kube-scheduler:v1.28.0
  command:
  - kube-scheduler
  - --config=/etc/kubernetes/my-scheduler-config.yaml  # <-- Yahan Engine ne settings padhi!

```

* **Final Destination:** Scheduler program ne wo text file padh li. Usko pata chal gaya ki *"Achha, mera naam `my-custom-scheduler` hai, aur mujhe default-scheduler ke kamo mein taang nahi adani hai."*

---

### 🧠 Short Summary of the Flow (Interview Pitch)

Agar interviewer puche: *"Explain the exact data flow of custom scheduler configuration."*

**The Perfect Answer:**
"Sir, the flow goes like this:

1. We write the Scheduler Configuration rules (like `schedulerName` and `leaderElect`) in a local YAML file.
2. We inject this raw text data into the Kubernetes cluster by creating a **ConfigMap**.
3. Inside our Custom Scheduler Deployment, we define a **Volume** that points to this ConfigMap, and a **VolumeMount** that projects this data as a physical file inside the container (e.g., at `/etc/kubernetes/config.yaml`).
4. Finally, the `kube-scheduler` binary running inside the container uses the `--config` flag to read that exact mounted file and starts operating with those specific settings."

---
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-custom-scheduler
  namespace: kube-system
spec:
  # ---------------------------------------------------------
  # PART 1: THE CONTAINER (Brain & Execution)
  # ---------------------------------------------------------
  containers:
  - name: my-custom-scheduler
    image: k8s.gcr.io/kube-scheduler:v1.28.0   # <-- (ye official image he basic scheduler work hone ke liye required ye like apne code ke liye required package kaise kam kartahe)
    command:
    - kube-scheduler
    - --config=/etc/kubernetes/my-scheduler-config.yaml
    volumeMounts:                              # <-- Container volume ko apne andar attach kar raha hai
    - name: config-volume                      # <-- Volume ka naam match hona chahiye!
      mountPath: /etc/kubernetes/              # <-- Container ke andar is folder mein file aayegi

  # ---------------------------------------------------------
  # PART 2: THE VOLUME (The Delivery Boy)
  # ---------------------------------------------------------
  volumes:
  - name: config-volume                        # <-- Ye raha wo naam
    configMap:
      name: custom-scheduler-config            # <-- Ye wo ConfigMap hai jo tune pehle banaya tha

```
