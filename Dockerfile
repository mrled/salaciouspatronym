FROM public.ecr.aws/lambda/python:3.9
LABEL maintainer "me@micahrl.com"
RUN mkdir -p /usr/local/src/salpat
COPY . /usr/local/src/salpat
RUN true \
    && ls -alF /usr/local/src/salpat /usr/local/src/salpat/salaciouspatronym \
    && umask 022 \
    && find /usr/local/src/salpat -exec chmod a+rX {} \; \
    && python3 -m pip install --upgrade pip \
    && python3 -m pip install /usr/local/src/salpat \
    && ls -alF /var/lang/lib/python3.*/site-packages/salaciouspatronym \
    && rm -rf /usr/local/src/salpat \
    && true
CMD ["salaciouspatronym.aws_lambda_handler"]
