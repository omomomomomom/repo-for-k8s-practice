Ye le bhai, tere **Kubernetes Certification (CKA/CKAD)** ke liye perfect **Cheat Sheet** ready hai.

Isme maine saare **Imperative Commands** ko organize kar diya hai taaki tu exam mein copy-paste ya ratta maar sake. Isko `kubectl-imperative-cheatsheet.md` naam se save kar lena.

```markdown
# 🚀 Certification Tips: Imperative Commands with Kubectl

While you would be working mostly the **Declarative way** (using definition files), **Imperative commands** can help in getting one-time tasks done quickly, as well as generating a definition template easily.

**Why is this important?**
This saves a considerable amount of time during CKA/CKAD exams where every minute counts!

---

## ⚡ The "Magic" Flags
Before we begin, memorize these two options. They are your best friends in the exam.

### 1. `--dry-run=client`
By default, as soon as a command is run, the resource will be created.
* If you simply want to **test** your command or generate a template, use this.
* It tells you if your command is right without actually creating anything.

### 2. `-o yaml`
* This outputs the resource definition in **YAML format** on the screen.

> **Pro Tip:** Use them together to generate a file quickly!
> `command + --dry-run=client + -o yaml > filename.yaml`

---

## 📦 POD Commands

### Create an NGINX Pod (Directly)
```bash
kubectl run nginx --image=nginx

```

### Generate POD Manifest YAML (Don't Create)

Use this to get the YAML structure, then modify it if needed.

```bash
kubectl run nginx --image=nginx --dry-run=client -o yaml

```

---

## 🚀 Deployment Commands

### Create a Deployment

```bash
kubectl create deployment --image=nginx nginx

```

### Generate Deployment YAML (Don't Create)

```bash
kubectl create deployment --image=nginx nginx --dry-run=client -o yaml

```

### Create Deployment with 4 Replicas

```bash
kubectl create deployment nginx --image=nginx --replicas=4

```

### Scale a Deployment

You can scale an existing deployment using the `scale` command.

```bash
kubectl scale deployment nginx --replicas=4

```

### Generate YAML to a File (Best Practice)

Save the definition to a file, modify it, and then create it.

```bash
kubectl create deployment nginx --image=nginx --dry-run=client -o yaml > nginx-deployment.yaml

```

*After running this, open `nginx-deployment.yaml`, edit the replicas or image, and run `kubectl apply -f nginx-deployment.yaml`.*

---

## 🌐 Service Commands

### 1. ClusterIP Service (Expose a Pod)

**Option A: Using `expose` (Recommended)**
This automatically uses the pod's labels as selectors.

```bash
kubectl expose pod redis --port=6379 --name redis-service --dry-run=client -o yaml

```

**Option B: Using `create service**`
⚠️ **Warning:** This assumes `app=redis` selectors and ignores actual pod labels. You cannot pass selectors as an option here.

```bash
kubectl create service clusterip redis --tcp=6379:6379 --dry-run=client -o yaml

```

---

### 2. NodePort Service

**Option A: Using `expose` (Recommended)**
This automatically uses the pod's labels, but you **cannot specify the NodePort** directly here.

```bash
kubectl expose pod nginx --type=NodePort --port=80 --name=nginx-service --dry-run=client -o yaml

```

> **Tip:** Generate the file using this command, then open the YAML and manually add `nodePort: 30080` under `ports`.

**Option B: Using `create service**`
This allows specifying NodePort but **does not use the pod's labels** correctly as selectors.

```bash
kubectl create service nodeport nginx --tcp=80:80 --node-port=30080 --dry-run=client -o yaml

```

### 💡 Recommendation for Services

I would recommend going with the **`kubectl expose`** command.
If you need to specify a **NodePort**, generate a definition file using the command and **manually input the nodePort** in the YAML before creating the service.

---

## 📚 References

* [Kubectl Command Reference](https://kubernetes.io/docs/reference/generated/kubectl/kubectl-commands)
* [Kubectl Conventions](https://kubernetes.io/docs/reference/kubectl/conventions/)

```

```


Iska main maksad ye hai: **"Agar internet nahi chal raha, ya browser kholne ka time nahi hai, to Terminal ke andar hi help kaise lein?"**

Kubernetes ke paas apni khud ki **Built-in Dictionary/Documentation** hoti hai. Ye lecture usi ko use karne ke **2 Main Commands** sikha raha hai:

---

### 1. `kubectl api-resources` (Resource Dhundne ke liye) 🕵️‍♂️

**Problem:**
Kabhi-kabhi hum bhool jate hain ki:

* Resource ka sahi naam kya hai? (`pods` hai ya `pod`?)
* Uska **Short Name** kya hai? (`po`, `svc`, `deploy`?)
* Uska **API Version** kya hai? (Deployments ke liye `v1` use karein ya `apps/v1`?)
* Kya ye resource **Namespaced** hai ya nahi?

**Solution:**
Bas ye command chalao:

```bash
kubectl api-resources

```

Ye ek list nikaal ke dega jisme saari details hongi.

* Example: Tumhein dikhega `pods`, uska short name `po`, version `v1`, aur `namespaced=true`.

---

### 2. `kubectl explain` (YAML likhne ke liye) 📝

**Problem:**
Tumhein pata hai ki `Pod` banana hai, lekin tum bhool gaye ki YAML file mein `spec` ke andar kya aata hai? `containers` likhna hai ya `container`? `image` kahan likhna hai?

**Solution:**
`kubectl explain` command tumhari help karegi. Iske 3 levels hain:

#### Level 1: Upar-Upar se dekhna (Top Level)

Jab tum ye chalate ho:

```bash
kubectl explain pods

```

To ye batayega ki Pod ke main parts kya hain: `apiVersion`, `kind`, `metadata`, `spec`, `status`.
(Jaise kitaab ke chapters ke naam dekhna).

#### Level 2: Detail mein ghusna (Drill Down) ⛏️

Agar tumhein `spec` ke andar kya aata hai wo dekhna hai, to **dot (`.`)** lagao:

```bash
kubectl explain pods.spec

```

Ab ye `spec` ke andar ki saari cheezein dikhayega (jaise `containers`, `volumes`, `nodeName`).

Aur andar jaana hai?

```bash
kubectl explain pods.spec.containers

```

#### Level 3: Sab kuch ek sath dekhna (Recursive Mode) 🤯

Agar tumhein ek baar mein **Pura ka Pura Structure** dekhna hai (taaki tum YAML copy kar sako), to `--recursive` flag lagao:

```bash
kubectl explain pods --recursive

```

Ye puri hierarchy (tree structure) print kar dega. Ye tab kaam aata hai jab tum complex YAML file likh rahe ho aur internet access nahi hai.

---

### Summary in Simple Hindi:

1. **Naam ya Version bhool gaye?** -> `kubectl api-resources` use karo.
2. **YAML fields bhool gaye?** -> `kubectl explain <resource>` use karo.
3. **Specific field check karna hai?** -> `kubectl explain pod.spec` (Dot lagao).
4. **Puri janm-kundali dekhni hai?** -> `kubectl explain pod --recursive` use karo.