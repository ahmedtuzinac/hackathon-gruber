### Hackathon 2024

#### Team name: Cube

#### Project name: RouteBOT

#### DateTime: 2024-11-09 14:30

# Backend installation guide

1. Checkout project

``` bash
git clone https://github.com/ahmedtuzinac/hackathon-gruber
``` 

2. Checkout to main branch

``` bash
git checkout main
``` 

3. Install virtual environment python3.11+ and activate it

``` bash
python3.12 -m venv .venv
source .venv/bin/activate
``` 

4. Install requirements

``` bash
pip install -r requirements.txt
``` 

5. Populate .env file (sample is on repo)
6. Make source as a source root directory
7. Start service with python service.py and enjoy

``` bash
python service.py &(optional)
``` 

# Frontend installation guid

1. Install dependencies

``` bash
npm install
```

2. Create proxy.conf.json from the proxy.conf.sample.json

3. Start application locally
``` bash
npm run start
```



