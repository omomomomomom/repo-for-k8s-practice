
---

# 🚦 Kubernetes Priority Classes & Preemption (DevOps Interview Notes)

### 🧠 1. Concept (Aasan Bhasha Mein)

Maan le ek bohot popular Club (Tera K8s Node) hai jo poora full hai.

* **Normal Log (Default Pods):** Line mein khade hain (Queue).
* **VIP (High Priority Pod):** Aata hai, bouncer ko pass dikhata hai, aur bouncer andar se kisi "Normal bande" ko dhakka maar ke bahar nikal deta hai taaki VIP ko table mil sake. Is dhakka maarne ko **"Preemption"** bolte hain.
* **Club Owner (System Critical Pods):** Inka level sabse upar hai, inko koi nahi chhu sakta (Kube-system components).

**Priority Class** ek VVIP pass hai jo tu apne pods ko deta hai taaki unhe scheduling mein priority mile.

---

### 🎯 2. The "Why" (Technical Reason & Use Cases)

**Bina Priority Class ke kya hoga?**
Agar tera cluster full hai aur ek critical Payment Gateway ka pod schedule hona hai, to wo `Pending` state mein pada rahega jab tak koi doosra pod apna kaam khatam karke resources free nahi karta. Business ka nuksan ho jayega!

**The Technical Solution:**
Hum K8s ko batate hain ki "Payment App" ki priority "Background Email Job" se zyada hai.

* Agar cluster full hua, to K8s chup-chaap Email Job wale pod ko **kill (evict)** kar dega aur Payment App ko uski jagah bitha dega.
* Isme number game hota hai: **Bada Number = Badi Priority**.

---

### 💻 3. Practical Example & Code Breakdown

Sabse pehle humein ek "Pass" (PriorityClass) banana padta hai, uske baad wo pass Pod ko dena padta hai.

#### Step 1: Create PriorityClass (The VVIP Pass)

```yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: high-priority-payment          # <--- Pass ka naam
value: 1000000                         # <--- Priority value (Higher = Better)
globalDefault: false                   # <--- Agar 'true' kiya, to sabhi naye pods ko by default ye mil jayega
description: "Used for Critical Payment Microservices"
preemptionPolicy: PreemptLowerPriority # <--- (Default) Ye lower pods ko kill kar dega
# preemptionPolicy: Never              # <--- Agar kill nahi karna, bas line mein aage khada hona hai

```

*(Apply with `kubectl apply -f priority-class.yaml`)*

#### Step 2: Attach to Pod (Pass the VIP Ticket)

Ab pod banate waqt `spec` ke andar `priorityClassName` mention kar do.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: payment-backend
spec:
  containers:
  - name: my-app
    image: payment-app:v1
  priorityClassName: high-priority-payment  # <--- Pod ko VVIP pass mil gaya!

```

---

### 🔥 4. DevOps Interview Q&A (Interviewer's Trap)

**Q1: Are Priority Classes Namespaced? Can I create a Priority Class specifically for the `dev` namespace?**

* **The Perfect Answer (Trap Alert 🚨):** "No, PriorityClasses are **non-namespaced** (cluster-scoped) objects. Once created, they can be assigned to any pod in any namespace across the entire cluster."

**Q2: What happens if a Pod doesn't have a PriorityClass defined? What is its default priority?**

* **The Perfect Answer:** "By default, any pod without a specific PriorityClass gets a priority value of **0**. However, as administrators, we can change this by creating a PriorityClass and setting `globalDefault: true`. Only one PriorityClass in the entire cluster can have `globalDefault` set to true."

**Q3: I want to give my application the absolute highest priority possible. Can I set the value to 2 Billion?**

* **The Perfect Answer:** "No, we shouldn't do that. The range around positive 2 Billion is strictly reserved for internal Kubernetes control plane components (like `system-cluster-critical` and `system-node-critical`). If we assign that to our user apps, we risk evicting critical system pods like `kube-proxy` or `coreDNS`, which will crash the cluster. For user workloads, we should stick to numbers up to 1 Billion."

**Q4: I want my high-priority pod to jump to the front of the scheduling queue, but I DON'T want it to kill (evict) any currently running lower-priority pods. How do I achieve this?**

* **The Perfect Answer:** "We can achieve this by setting the `preemptionPolicy: Never` inside the PriorityClass definition. This makes the pod non-preempting. It will wait for resources to free up naturally, but it will be scheduled *before* other lower-priority pods that are also waiting in the queue."

Lo bhai, isko ekdum mast format kar diya hai tumhare notes ke "DevOps Interview Q&A" section ke liye. Seedha copy-paste maar lena apni `.md` file mein!

---

### 🔥 DevOps Interview Q&A: Priority Classes

**Q1: What happens if a Pod doesn't have a PriorityClass defined? What is its default priority?**

* **The Perfect Answer:** "By default, any pod without a specific PriorityClass gets a priority value of `0`. However, as administrators, we can change this cluster-wide default by creating a PriorityClass and setting `globalDefault: true`."

**Q2: Can I create three different PriorityClasses and set `globalDefault: true` on all of them?**

* **The Perfect Answer (Trap Alert 🚨):** "No, sir. We can only have exactly **ONE** PriorityClass in the entire Kubernetes cluster with `globalDefault: true`. If we try to create a second one, the Kube API Server will reject it. You cannot have multiple defaults."

**Q3: Are Priority Classes Namespaced? Can I create a Priority Class specifically for the `dev` namespace?**

* **The Perfect Answer:** "No, PriorityClasses are **non-namespaced (cluster-scoped)** objects. Once created, they apply across the entire cluster."

**Q4: I want my high-priority pod to jump to the front of the queue, but I DON'T want it to kill (evict) any running pods. How?**

* **The Perfect Answer:** "We set `preemptionPolicy: Never` inside the PriorityClass definition. This makes the pod non-preempting. It will wait for resources to free up naturally, but it will be scheduled *before* other lower-priority pods that are also waiting in the queue."

---
 
---

