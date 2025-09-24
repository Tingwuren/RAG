FROM python:3.10
WORKDIR /app
COPY install_gpu_pytorch.py ./
RUN python install_gpu_pytorch.py
COPY requirements.txt ./
RUN pip install -r requirements.txt -i https://mirrors.ustc.edu.cn/pypi/web/simple
COPY download_model.py ./
RUN python download_model.py
COPY ./app /app/app
COPY run.py .
CMD ["python", "run.py"]
