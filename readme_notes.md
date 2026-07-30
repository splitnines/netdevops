1. Write a description of the project as an introduction.  Note how the project is meant to be modular and each unit is optional.
2. Describe how to clone the repo and set up the enviroment using uv
3. Describe the workflow below
  a. Create a new git branch
  b. Configure the ansible environment
    i. Create or copy a backup playbook into the playbooks directory (option)
    i. Create a new or use an existing inventory and group_vars
    ii. Create or copy an existing playbook to the playbooks directory
  c. Configure the pyATS environment (optional)
    i. Modify or replace the job.py file in the tests direcory
    ii. Create or copy test_suites and test_script.
      1. The job.py calls the test_suite script which calls one or more test_scripts
4. Add and commit the changes to local git branch
5. Push the git branch to the remote.
6. Github tracks the status of the worker and will report the success/failer of each of the pipeline steps.
