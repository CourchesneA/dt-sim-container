all: build

build:
	docker build -t courchesnea/dt-sim:test .

run:
	docker run courchesnea/dt-sim:test 
