
# # Use the official Python image as the base image
# FROM python:3.10-slim

# # Set the working directory inside the container
# WORKDIR /app

# # Copy the current directory contents (including app.py and requirements.txt) into the container at /app
# COPY ./python/. /app

# # Install Flask (and any other dependencies you list in requirements.txt)
# RUN pip install --no-cache-dir -r requirements.txt

# # Expose port 5000 (the default Flask port)
# EXPOSE 5000

# # Define the command to run your Flask app
# CMD ["flask", "run", "--host=0.0.0.0"]


# Use a base image with GCC for ARM64 architecture
FROM docker.io/gcc:14.2

WORKDIR /home/crunch_user

# Install build dependencies
RUN apt-get update && apt-get install -y \
    liblapack-dev python3 python3-pip git make cmake wget && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set environment variables for PETSc
ENV PETSC_DIR=/home/crunch_user/petsc
ENV PETSC_ARCH=arch-linux-c-opt

# Set environment variables for PETSc
ENV PETSC_DIR=/home/crunch_user/petsc
ENV PETSC_ARCH=arch-linux-c-opt

# Clone, configure, build, and clean up PETSc
RUN git clone https://gitlab.com/petsc/petsc.git $PETSC_DIR && \
    cd $PETSC_DIR && \
    git checkout v3.21.6 && \
    ./configure --with-cc=gcc --with-cxx=g++ --with-fc=gfortran \
                --with-debugging=0 --with-shared-libraries=0 \
                --with-x=0 LIBS=-lstdc++ --with-c2html=0 \
                --with-cxx-dialect=C++11 --with-mpi=0 && \
    make PETSC_DIR=$PETSC_DIR PETSC_ARCH=$PETSC_ARCH all && \
    make PETSC_DIR=$PETSC_DIR PETSC_ARCH=$PETSC_ARCH check && \
    rm -rf $PETSC_DIR/src $PETSC_DIR/arch-$PETSC_ARCH/conf \
           $PETSC_DIR/arch-$PETSC_ARCH/tests $PETSC_DIR/arch-$PETSC_ARCH/share

# Download, build, and clean up CrunchTope
WORKDIR /home/crunch_user
RUN wget https://github.com/CISteefel/CrunchTope/releases/download/v2.10/CrunchTope-2.10.tar.gz && \
    tar -xvzf CrunchTope-2.10.tar.gz && \
    rm CrunchTope-2.10.tar.gz && \
    mv CrunchTope-2.10 crunchtope && \
    cd crunchtope && \
    make && \
    rm -rf /home/crunch_user/crunchtope/*.o /home/crunch_user/crunchtope/Makefile \
           /home/crunch_user/crunchtope/*f.90 && \
    rm -rf /home/crunch_user/petsc

# Add CrunchTope to PATH
ENV PATH="/home/crunch_user/crunchtope:${PATH}"

# Install Python tools
RUN pip3 install --no-cache-dir --break-system-packages \
    jupyterlab \
    crunchflow==2.0.4 \
    pyDGSA==1.0.5 \
    pyEMU==1.3.5 

# WORKDIR /app
COPY ./python/. /app
RUN pip3 install --no-cache-dir --break-system-packages \ 
    Flask==2.0.3 \
    werkzeug==2.0.3 \
    qiskit==1.2.4 \
    qiskit-aer==0.15.1 \
    numpy==1.26.4

# Expose port 5000 (the default Flask port)
EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0"]

# Final working directory
WORKDIR /home/crunch_user
