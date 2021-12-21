# Salacious Patronym

turns out i have a very juvenile sense of humor

Salacious Patronym is a Twitter bot that turns names into jokes, such as

> Barrack's "Obama" 🍆

or

> Hillary's "Clinton" 😏

or

> George's "Bush" 💦

See it over at [@SalaciousPat](https://twitter.com/SalaciousPat)

## Installing and running locally

Requires Python 3.x and [tweepy](http://tweepy.readthedocs.io/en/v3.5.0/)

I tend to use `virtualenv` to manage third party Python libraries:

```sh
python3 -m venv venv
. venv/bin/activate
pip install -e .
```

I have some tests (ok fine, I have one test) that can be run with the built-in `unittest` module:

```sh
python -m unittest discover
```

After activating the virtual environment and installing the package with `pip` per above:

```sh
salaciouspatronym --help
```

## Testing AWS Lambda running locally

Note that this will actually post to Twitter.

First, create an `env.txt` file with consumer/app token/secrets.
It might look like this:

```sh
SALLYPAT_CONSUMERTOKEN=qwer...
SALLYPAT_CONSUMERSECRET=asdf...
SALLYPAT_ACCESSTOKEN=1234-zxcv...
SALLYPAT_ACCESSSECRET=yuio...
```

Then build and run the docker container:

```sh
docker build -t sallypat . && docker run --env-file env.txt -p 9000:8080 sallypat
```

Finally, send an empty event to the container:

```sh
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}'
```

## Deploying to AWS Lambda

This is how we deploy to Lambda

### Configure the ECR registry

This only has to be done once.

Taken from
<https://aws.amazon.com/blogs/aws/new-for-aws-lambda-container-image-support/>

```sh
reponame="salaciouspatronym"
aws ecr create-repository --repository-name "$reponame" --image-scanning-configuration scanOnPush=true
```

After that, run this to find the repo and push to it:

```sh
reponame="salaciouspatronym"
repouri="$(aws ecr describe-repositories --repository-name "$reponame" | jq -r .repositories[0].repositoryUri)"
repouribase="${repouri%/$reponame}"
docker build -t "$reponame:latest" .
docker tag "$reponame:latest" "${repouri}:latest"
aws ecr get-login-password | docker login --username AWS --password-stdin "$repouribase"
docker push "$repouri:latest"
```

Then deploy the image to Lambda following instructions at
<https://aws.amazon.com/blogs/aws/new-for-aws-lambda-container-image-support/>.

Note that you'll have to re-deploy through the console for every new version of the container image.

Once the function is created, set the environment variables for the consumer/access token/secret.

Finally, trigger it on a schedule in Amazon EventBridge.
