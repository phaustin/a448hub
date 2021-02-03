FROM phaustin/base-image:jan23

USER ${NB_USER}

RUN mkdir -p ${HOME}/work/data_readonly
RUN mkdir -p ${HOME}/work/data_share


RUN echo "conda activate ${CONDA_ENV}" >> ${HOME}/.bashrc
COPY jupyter_notebook_config.py /etc/jupyter/

WORKDIR ${HOME}/work

CMD ["jupyterhub-singleuser"]
