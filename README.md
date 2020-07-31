# Python blog hosted on google cloud appengine standard and using datastore

For various reasons I wanted to stop using wordpress and host my own blog and personal website using a custom solution coded by me, hosted on google appengine (python standard environment).

Using an SQL database is "cheap" but still costs a few bucks per month. So I decided to use google datastore, which has a free quota of 50'000 queries per month, then it costs still less than a real database.

## Getting started

- If you are new to Google Cloud, install the SDK, set up your environment and accounts as described in the [Quickstart for Python 3 in the App Engine Standard Environment](https://cloud.google.com/appengine/docs/standard/python3/quickstart) documentation. Make sure that you installed these components:
  - `core` (Cloud SDK Core Libraries)
  - `gsutil` (Cloud Storage Command Line Tool)
  - `beta` (gcloud Beta Commands)
  - `app-engine-python` (gcloud app Python Extensions)
  - `cloud-datastore-emulator` (Cloud Datastore Emulator)
- Clone this repository.

## Export your WordPress blog posts

In **phpMyAdmin** > export:
- **Export method**: select `Custom - display all possible options`
- **Format**: select `CSV`
- **Tables**: check just the `wp_posts` table

## Configure your blog settings

My solution expects a folder called `data` and a `settings.ini` file in it. Simply rename the `samples` folder to `data` and edit the `settings.ini` file in it.

## Import the CSV in a local SQLite database

This is work still in progress. In the meantime, if you know SQLalchemy, you know you can create an empty db because the model is ready (see `db_model.py`). I will automate this later on.

With [Jetbrains DataGrip](https://www.jetbrains.com/datagrip/) import the CSV in the wp_posts table.

This query was useful to me, to see all my blog posts:
```
select * from wp_posts
where post_status = 'publish'
  and post_type = 'post'
  and post_password = '';
```

This query was useful to me, to see all pages and other entities (menu items etc.):
```
select * from wp_posts
where post_status = 'publish'
  and post_type != 'post'
  and post_password = '';
```

## Configure appengine and the local test enviroment

Work in progress.

- Create service key for your appengine project and save it inside the `keys` folder.
- In a command line, run: `gcloud beta emulators datastore start`. Note the line that says (e.g. in my case) `export DATASTORE_EMULATOR_HOST=localhost:8081`
- In [Jetbrains pyCharm](https://www.jetbrains.com/pycharm/), open this git repository.
- Create a python environment when asked (select `python3.7`), or do it later if you skipped the step.
- Click on the `migrate.py` file and in the **Run** menu click on **Run** > **Edit Configurations** > in the **Environment Variables** set:
  - `GOOGLE_APPLICATION_CREDENTIALS`: path to the key file you saved inside the `keys` folder
  - `DATASTORE_PROJECT_ID`: your google cloud project id
  - `DATASTORE_EMULATOR_HOST`: the URL you see when you run `gcloud beta emulators datastore start` command, as described above
- Save the configuration with a name such as *migrate - test*.
- Duplicate the configuration and in the **Script path** rename `migrate.py` to `main.py` and name it e.g. *main - test*.
- Run the *migrate - test* configuration: this will save all your pages and posts from the sqlite database to your local emulated datastore.

## Test your blog locally ##

Run the *main - test configuration* created above.
- browse to http://localhost:8080
- browse to http://localhost:8080/admin/ to see the admin panel (to add and edit pages, posts and configurations). This works only after configuring correctly the authentication (see below: Set up Google Login).

## Set up Google Login

See [Google Login Flask tutorial](https://realpython.com/flask-google-login/).

Create a client for local testing purposes, then create one for your production website. The steps are the same. Just the URLs will differ if you use a different port and in prod, you will use your domain name.

Note, when you deploy your files in "prod", if you did not associate the app to a custom domain, you will have a domain similar to this: https://project-id.oa.r.appspot.com (you can see the URL in the [appengine dashboard](https://console.cloud.google.com/appengine), but only after deploying it for th first time).

In prod you can use this URL and also your custom domain name.

- Configure the consent screen for your project
  - In the `Authorized domains` add your domain(s), e.g. https://project-id.oa.r.appspot.com and also your custom domain.
- Create a [Google oauth client](https://console.developers.google.com/apis/credentials)
  - Name it e.g. `Test client`
  - URIs: `https://localhost:8080`
  - Authorized redirect URIs: `https://localhost:8080/login/callback`
  - Note client ID and secret somewhere safe (e.g. in a keepass encrypted file)
  - Set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in the Environment variables of your `main - test` configuration

Repeat the same process, later, for your production domain (you can re-use the same consent screen if you want, but it's a good idea to separate the test clint from the prod client).

## Depploy the app

- [Enable Cloud Build](https://console.developers.google.com/apis/api/cloudbuild.googleapis.com/overview) for your project (this requires you to associate your project to a billing account)
- Run `gcloud --project=PROJECT-ID datastore indexes create index.yaml` to create the necessary indexes for datastore
- Copy the `app.yaml` file to `data/app.yaml` (you can have several .yaml files for different environments/projects, so you can name the file accordingly) and set the client id and secret.
- Run `mv data/pbworks.yaml .; gcloud app deploy --project=pbworks ./pbworks.yaml; mv pbworks.yaml data/`
  - Note: if you specify the `app.yaml` file in a subfolder, it will deploy the contents of the subfolder where the yaml file is located, so I move the file in the app folder, deploy, then move it back to the data folder.
  - If it's the first deployment, you will see a screen allowing you the location where to host your app. Choose wisely, e.g. if you live in Europe, but your audience is mostly come from USA, choose a location in the US. check also [Cloud Locations](https://cloud.google.com/about/locations) and see which products are available, e.g. I chose `us-east4`. You can also check the cost. But if you plan to host a small website with not many hits, the const will be free anyway.

## Various

To fix the page displayed in the home, the page slug must be `home`. In my case the homepage slug was `sample-page` (from an old WordPress installation, where I edited the content of the existing sample-page to make my home). To do so, browse to the `admin` area > `Edit posts` > Edit the page > name the slug `home`.

## Errors/Debugging

https://console.cloud.google.com/errors

## Work in progress ##

This project is heavily work in progress. Use it at your own risk. This documentation needs to be tested and rewritten. If in the meantime you test this and it works for you, please drop me a line in the Issues page, feedback is always welcome.