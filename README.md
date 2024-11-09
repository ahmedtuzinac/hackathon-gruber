<span >Project: </span><span style="color: #78866b;">FastApi monolith application template</span>
<br>
<span >Stacks: </span><span style="color: #78866b;">FastApi / Python3.12</span>
<br>
<span >Author: </span><span style="color: #78866b;">Digital Cube d.o.o</span>

# Installation
 ### 1. Clone project 
    git clone git@github.com:ijdigital/svctpl.git 

 ### 2. Create virtual environment and install requirements.
Create virtual environment.

    cd svctpl/
    python3.12 -m venv .venv
    source .venv/bin/activate
Install requirements:
    
    pip install -r requirements.txt
 ### 3. Mark source directory
  We will find /src/ directory in the project.
  <br>Mark this directory as sources root.

  PyCharm:

    Right click on /src/ and select 'Mark Directory as' and select 'Sources Root'.
    Excpected output should be changed color of /src/ directory to blue.

   Command Line (usually used when we develop/deploy project on server):

    cd svctpl
    cd src/
    pwd (copy working directory) 
    
    joe .venv/lib/python3.12/site-packages/custompaths.pth
        Paste here copied value (pwd of /src/)
        Save it and exit.
    
    Restart virtual environment.
    deactivate 
    source .venv/bin/activate

 ### 4. Set environment file
In project you will find env.sample file. Create .env file from env.sample
<br> and populate values. 






### Note: 

<span style="color: #78866b;">In /tests/__init__.py you can specify which database engine you want to use, 'psql' or 'sqlite', by default it'll be psql. 
<br>If you chose psql for now you will have to create manually databases, <database_name> and test_<database_name>. In next release we hope that will not be necessary.</span>



        
        

