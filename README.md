# Manifest, krant van de NCPN website

Code for site at: http://manifest.ncpn.nl

Tip: You could use [retext](https://github.com/retext-project/retext) to make changes to this file.

## Getting started

1. As root install sudo: `apt install sudo` and add your user name to the sudo group: `sudo vigr`

- The rest of the commands you can do logged in with your normal user id.
- Install postgresql: `apt install postgresql libpqxx-dev` and configure:
- - become the postgres superuser: `sudo su - postgres`
- - create the database: `createdb manifest`
- - Get a sql session: `psql`
- - Create a user: `create user manifest;`
- - Define a password to it: \password manifest
- - Type the password twice, you will see nothing echoed: `manifest` for dev
- - Define the user's privileges: `grant all on database manifest to manifest;`
- - end your sql session: `exit` of `<C-D>` (which is the Linux eof character)
- - end your session as postgres superuser: `exit` or eof (end-of-file character)

- Install git and python3:<br>
`apt install git python3 virtualenvwrapper`
- Add a line to the end of your bash startup file:<br>
`echo 'source /usr/share/virtualenvwrapper/virtualenvwrapper.sh' >> ~/.bashrc`
- - Prepare the way virtualwrapper will work for you (you will need to do this setup only once):
- - - `echo 'folder=$(echo $VIRTUAL_ENV| sed "s/\.virtualenvs/py/")' >> ~/.virtualenvs/postactivate`
- - - `echo 'mkdir -p $folder' >> ~/.virtualenvs/postactivate`
- - - `echo 'cd $folder' >> ~/.virtualenvs/postactivate`

- - Make a python virtual environment: `mkvirtualenv manifest` (This will probably fail because virtualwrapper has not started properly because you were installing it: log out and log in and try again.)<br>
With this setup you will `pip install ...` your python libraries in `~/.virtualenvs` and your working folders in `~/py`.

- - Clone the git repository from your current folder (~/py/manifest and still inside the manifest python environment:<br>
`git clone git@github.com:communistische-partij-nederland/manifest.git .` (don't forget the dot at the end to use the current folder as the clone target rather then the default target folder which would be an extra subfolder `manifest` in this case.)

- - Install the software, and the dev tooling:<br>
   `pip install -r requirements.txt -r requirements-dev.txt`

- - Build the Sass:<br>
   `python manage.py sass -g website/static/website/src/custom.scss website/static/website/css/`<br>
   To build the Sass automatically whenever you change a file, add the `--watch`
   option and run it in a separate terminal. To build a compressed/minified
   production version, add the `-t compressed` option. For more options, see
   [django-sass](https://github.com/coderedcorp/django-sass/).

- Run the development server:<br>
   `python manage.py runserver` or, a bit shorter: `./manage.py runserver`

- you should see that you need to apply migrations, do that now:<br>
Kill your development server by typing `<C-C>` and run migrations:<br>
`./manage.py migrate` Then start your development server again.

- Go to `http://localhost:8000/` in your browser, or `http://localhost:8000/admin/` to log in and get to work!

## How to deploy to production server 

Go to folder:
```
cd /var/www/manifest
```

First, get into the virtual environment
```
source venv/bin/activate
```

Go one level down
```
cd manifest
```

Pull all changes
```
git pull origin master
```

Then, install all requirements:
```
 pip3 install -r requirements.txt
```

Compile sass code
```
python3 manage.py sass website/static/website/src/custom.scss website/static/website/css/custom.css
```

Collect all static files
```
python3 manage.py collectstatic
```

Restart python
```
sudo systemctl restart uwsgi
```

## Documentation links

* To customize the content, design, and features of the site see
  [CodeRed CMS](https://docs.coderedcorp.com/cms/).

* For deeper customization of backend code see
  [Wagtail](http://docs.wagtail.io/) and
  [Django](https://docs.djangoproject.com/).

* For HTML template design see [Bootstrap](https://getbootstrap.com/).

---

Made with ♥ using [Wagtail](https://wagtail.io/) +
[CodeRed CMS](https://www.coderedcorp.com/cms/)
