
---

# 🛂 Kubernetes Admission Controllers (DevOps Interview Notes)

### 🧠 1. Concept: The Kubernetes Security Pipeline (Aasan Bhasha Mein)

Soch ki Kubernetes ka API Server ek **Highly Secure Airport** hai. Jab tu `kubectl run pod` command chalata hai, to tera request 3 security gates se guzarta hai:

1. **Gate 1: Authentication (ID Card Check):** K8s check karta hai ki "Tu kaun hai?" (Certificates, User ID via kubeconfig).
2. **Gate 2: Authorization (Boarding Pass Check):** K8s check karta hai "Kya tere paas Pod banane ki permission hai?" (Ye kaam **RBAC - Role Based Access Control** karta hai).
3. **Gate 3: Admission Controller (Luggage Check):** Ye sabse strict gate hai. Permission hone ke baad bhi, ye tere Pod ki YAML file (samaan) ko khol ke dekhta hai ki andar koi illegal cheez to nahi hai! Agar sab sahi hai, tabhi data **etcd** database mein save hota hai.

---

### 🎯 2. The "Why": RBAC vs Admission Controllers

**Sabse bada sawal: Jab RBAC hai, to Admission Controller kyu chahiye?**

* **RBAC ki aukaat (Limitations):** RBAC sirf itna bol sakta hai ki *"Developer 'blue' namespace mein Pods bana sakta hai."* * **The Problem:** RBAC tere pod ke **andar ka content** nahi padh sakta. Developer chalaak ho sakta hai. Wo ek aisa pod bana sakta hai jo `root` user ki tarah run ho raha ho, ya aisi image use kar raha ho jo insecure ho (jaise `nginx:latest`).
* **The Solution (Admission Controllers):** Admission controllers object ke content ko validate kar sakte hain. Ye aisi strict policies enforce kar sakte hain:
* *"Bhai, pod mein `latest` image tag allow nahi hai."*
* *"Pod ko hamesha Non-Root user ki tarah chalna padega."*
* *"Har pod ke metadata mein 'Environment=Prod/Dev' ka label hona mandatory hai."*



---

### 🧰 3. Types of Pre-Built Admission Controllers

Kubernetes mein pehle se kuch "Security Guards" (Plugins) aate hain. Transcript mein inka zikr hai:

1. **`AlwaysPullImages`:** Ye make sure karta hai ki har baar naya pod banne pe image dubara pull ho (taaki koi purani cached insecure image use na ho).
2. **`DefaultStorageClass`:** Agar tune PVC banate waqt storage class ka naam nahi diya, to ye background mein aake chup-chaap default class ka naam YAML mein add kar deta hai (Isko Mutating bolte hain - request change karna).
3. **`EventRateLimit`:** Ye API server ko flood hone (DDoS attack) se bachata hai by limiting API requests.

---

### 🏛️ 4. The Namespace Story (A Classic Example)

Transcript mein bataya gaya hai ki Admission Controllers request ko **Reject** bhi kar sakte hain aur **Modify (Change)** bhi kar sakte hain.

* **Scene 1 (Reject): `NamespaceExists` Controller**
* Tune pod banaya `namespace: blue` mein. Par blue namespace exist hi nahi karta.
* Ye controller bolega: *"Namespace nahi hai, niklo yahan se!"* (Request Denied).


* **Scene 2 (Modify/Action): `NamespaceAutoProvision` Controller**
* Tune pod banaya `namespace: blue` mein.
* Ye controller bolega: *"Achha, blue namespace nahi hai? Ruko, main pehle background mein naya namespace bana deta hu, fir tera pod usme daal dunga."* (Request Accepted & Modified).



🚨 **BADA UPDATE (Deprecation Alert):**
Ab ye dono (NamespaceExists aur NamespaceAutoProvision) purane ho chuke hain (deprecated). Aajkal inki jagah ek naya smart guard aagaya hai: **`NamespaceLifecycle`**.
Ye naya guard 2 kaam karta hai:

1. Non-existent namespace mein pod nahi banne deta.
2. Sabse important: Ye tujhe default namespaces (`default`, `kube-system`, `kube-public`) ko **delete karne se rokta hai** taaki tu galti se cluster na uda de!

---

### 💻 5. Practical Commands (Check, Enable, Disable)

**Q: Kaise pata karein ki mere cluster mein kaunse guards (plugins) active hain?**
Kubeadm setup mein, API server ek Pod ke andar chalta hai. Tujhe `exec` karke help command se list nikalni padti hai:

```bash
kubectl exec kube-apiserver-controlplane -n kube-system -- kube-apiserver -h | grep enable-admission-plugins

```

**Q: Naya Guard (Controller) kaise Enable ya Disable karein?**
Tujhe master node ke andar SSH karke Static Pod ki file (`/etc/kubernetes/manifests/kube-apiserver.yaml`) ko edit karna padega. Usme ye flags add/update karne hote hain:

```yaml
spec:
  containers:
  - command:
    - kube-apiserver
    # Yahan comma-separated list mein naye controllers add ya remove karo
    - --enable-admission-plugins=NodeRestriction,NamespaceLifecycle,AlwaysPullImages
    - --disable-admission-plugins=DefaultStorageClass

```

*(Jaise hi tu is file ko save karega, API server auto-restart hoga aur naye rules apply ho jayenge).*

---

### 🔥 6. DevOps Interview Q&A (The Trap)

**Q1: We already use RBAC to restrict developers from deleting production pods. Why do we need Admission Controllers?**

* **The Perfect Answer:** "RBAC only checks *who* is making the request and *what* action they want to perform on an endpoint. However, RBAC cannot inspect the *content* of the request payload. Admission Controllers step in after RBAC to validate the actual YAML configuration—for example, preventing pods from running as root, enforcing specific labels, or rejecting images from public registries. They provide fine-grained, payload-level security."

**Q2: What is the difference between how `NamespaceExists` and `NamespaceAutoProvision` handled requests?**

* **The Perfect Answer:** "`NamespaceExists` was a purely validating controller; if the namespace wasn't there, it simply rejected the pod creation. `NamespaceAutoProvision`, on the other hand, was capable of performing additional backend operations; it would intercept the request, automatically create the missing namespace, and then allow the pod to be created."

**Q3: Can a user accidentally delete the `kube-system` namespace if they have cluster-admin rights?**

* **The Perfect Answer:** "No, they cannot. Even if RBAC allows the action, the default **`NamespaceLifecycle`** admission controller protects the core system namespaces (`default`, `kube-system`, `kube-public`) from being deleted. It will intercept the deletion request and reject it."

---

# *kubernetes-image-policy-webhook-lab*

---

# 🛡️ ImagePolicyWebhook Execution (The Complete Flow)

### 🧠 1. The Architecture (Kaun Kya Kar Raha Hai?)

Isme 3 main characters hain. Unka flow aise chalta hai:

1. **The User (Tu):** `kubectl run` command chalata hai ek Nginx pod banane ke liye.
2. **The Kube API Server (The Police):** Request ko pakadta hai. Usne dekha ki `ImagePolicyWebhook` plugin ON hai. To wo pod ko banne se rok deta hai (Hold pe daal deta hai).
3. **The External Scanner (The Expert):** API server ek JSON request banata hai aur tere diye hue URL (`https://image-checker-webhook.default.svc:1323/image_policy`) par bhejta hai. Ye scanner image ko check karta hai (Vulnerabilities, Tags) aur API server ko wapas reply karta hai: `"Allowed: True"` ya `"Allowed: False"`.

---

### 💻 2. Step-by-Step Execution (The Lab Setup)

Lab mein `/etc/kubernetes/imgvalidation` folder ke andar do (2) files hongi jinhe tujhe fix karna hai, aur fir API server ko restart karna hai.

#### Step 1: Webhook ka "Kubeconfig" banana (The Destination)

API server ko external scanner ka URL aise hi nahi de sakte. Usko ek `kubeconfig` format mein dena padta hai.
Lab mein ek file hogi (maan le `webhook.yaml` ya `kubeconfig.yaml`). Usko edit kar aur ye URL daal:

**File: `/etc/kubernetes/imgvalidation/webhook.yaml**`

```yaml
apiVersion: v1
kind: Config
clusters:
- cluster:
    server: https://image-checker-webhook.default.svc:1323/image_policy  # <--- Asli URL yahan aayega
    certificate-authority-data: "..." # (Lab mein pehle se hoga)
  name: image-checker
users:
- name: api-server
  user:
    client-certificate-data: "..." # (Lab mein pehle se hoga)
contexts:
- context:
    cluster: image-checker
    user: api-server
  name: image-checker-context
current-context: image-checker-context

```

#### Step 2: Admission Configuration banana (The Glue)

Ab API server ko batana padega ki `ImagePolicyWebhook` ka rule kahan likha hai. Iske liye ek master config file banti hai jo Step 1 wali file ko point karti hai.

**File: `/etc/kubernetes/imgvalidation/admission-config.yaml**`

```yaml
apiVersion: apiserver.config.k8s.io/v1
kind: AdmissionConfiguration
plugins:
- name: ImagePolicyWebhook
  configuration:
    imagePolicy:
      kubeConfigFile: /etc/kubernetes/imgvalidation/webhook.yaml  # <--- Step 1 wali file ka rasta!
      allowTTL: 50
      denyTTL: 50
      retryBackoff: 500
      defaultAllow: false  # <--- (Strict mode: Agar scanner fail hua, to pod mat banne do)

```

#### Step 3: Kube API Server ko activate karna (The Final Boss)

Ab master node ke `/etc/kubernetes/manifests/kube-apiserver.yaml` mein jake API server ko bolna hai ki in files ko padhe.

File khol `vi /etc/kubernetes/manifests/kube-apiserver.yaml` aur ye 2 flags add kar (command section mein):

```yaml
spec:
  containers:
  - command:
    - kube-apiserver
    # 1. Plugin ko ON karo
    - --enable-admission-plugins=NodeRestriction,ImagePolicyWebhook 
    # 2. Master Config file ka rasta do
    - --admission-control-config-file=/etc/kubernetes/imgvalidation/admission-config.yaml

```

*(Jaise hi tu is file ko save karke band karega, Kube API server automatically restart hoga. 1-2 minute wait karna padega).*

---

### 🎯 3. What Happens Next? (The Result)

Ab agar tu ek pod banayega jiski image mein koi vulnerability hai (jo scanner ko pasand nahi), to terminal pe error aayega:
`Error from server (Forbidden): pods "bad-pod" is forbidden: image policy webhook backend denied one or more images.`

Agar image clean hai, to pod normally `Running` state mein aa jayega.

---

### 🔥 4. DevOps Interview Q&A (The Trap)

**Q1: What is the difference between `ValidatingWebhookConfiguration` and `ImagePolicyWebhook`?**

* **The Perfect Answer:** "Both are used to validate requests via an external webhook, but `ImagePolicyWebhook` is specifically hardcoded and optimized just for container images. It is configured directly on the API server using local files (kubeconfig and admission-config). On the other hand, `ValidatingWebhookConfiguration` is a general-purpose, cluster-wide Kubernetes object (YAML) that can intercept *any* kind of resource (Pods, Deployments, Secrets, etc.) and is much more flexible."

**Q2: In the Admission Configuration, what does `defaultAllow: false` mean?**

* **The Perfect Answer (Trap Alert 🚨):** "This is a fail-open vs. fail-closed security concept. If the external image scanner service crashes or goes offline, the API server won't get a response. If `defaultAllow` is `false` (fail-closed), the API server will reject all new pod creations to be safe. If it is `true` (fail-open), it will allow pods to be created even if the scanner is dead, which is risky for security."

---

