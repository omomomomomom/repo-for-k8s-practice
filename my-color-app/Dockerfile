# 1. Base Image (Python ka chota version)
FROM python:3.9-slim

# 2. Working Directory set karna (Container ke andar ka folder)
WORKDIR /app

# 3. Pehle requirements copy karo aur install karo (Caching ke liye fast hota hai)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
#Note: --no-cache-dir option se pip cache nahi banata, jisse image size kam hota hai.

# 4. Ab baaki ka code copy karo
COPY app.py .

# 5. Default Environment Variables set karo
# (Agar humne kuch nahi bataya, to ye use honge)
ENV APP_COLOR=lightgreen
ENV APP_VERSION="v1-Base"

# 6. Port expose karo iskamatlab hai ki ye port container ke andar se bahar ke liye khula hoga
EXPOSE 5000

# 7. Command to run the app (using Gunicorn server) ye cmd par 
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]