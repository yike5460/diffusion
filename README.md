# local diffusion with API endpoint

- prepare a server, AWS EC2 P3 instance e.g.
- follow structions in [huggingface](https://github.com/huggingface/diffusers/tree/main#running-the-model-locally) to launch model in local
- launch daemon in server (flask e.g.) and curl through API to fetch generated images

```
curl -X POST -H "Content-Type: application/json" -d '{"prompt":"John is riding a horse", "output":"demo.png"}' http://ec2-xx-xx-xx-xx.us-west-2.compute.amazonaws.com:5003/api
```
