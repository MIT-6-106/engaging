.PHONY: ALL
ALL: autotester bayeselo pgnstats

.PHONY: autotester
autotester:
	cd autotester && $(MAKE)

.PHONY: pgnstats
pgnstats:
	cd pgnstats && $(MAKE)

.PHONY: bayeselo
bayeselo:
	cd BayesElo && $(MAKE)

referee:
	cp ../bin/referee ./referee

.PHONY: clean
clean:
	cd autotester && $(MAKE) clean
	cd BayesElo && $(MAKE) clean
	cd pgnstats && $(MAKE) clean

TEST_FILE := 
BATCH_ID := 

.PHONY: test
test: autotester bayeselo
	java -jar ./autotester/lauto.jar ../bin/referee $(TEST_FILE) $(BATCH_ID)
