CC := clang-6106

# You may not have the clang-6106 compiler i.e. 
# if you are running running on a platform other than Athena VDI.
#
# clang version 16 works here:
# - To run on Apple ARM CPUs, install Rosetta
# - To use cilk constructs, download the OpenCilk Clang at opencilk.org
# CC := clang

TARGET := leiserchess

SRC := leiserchess.c util.c tt.c fen.c move_gen.c search.c eval.c end_game.c board.c coords.c zob.c
OBJ := $(SRC:.c=.o)
DEP := $(OBJ:%.o=%.d)

UNAME := $(shell uname)
LOCAL := 0
ENGAGING := 0
DEBUG := 0
FLTO := 0
VERBOSE := 0

COMMONFLAGS := -Wall -Werror -Wextra
CFLAGS := $(COMMONFLAGS) -std=gnu99 -g
LDFLAGS := $(COMMONFLAGS) -fuse-ld=lld -static -pthread -lm -ldl

ifeq ($(PARALLEL),1)
	CFLAGS += -DPARALLEL -fopencilk
	LDFLAGS += -fopencilk
endif

# for Cilksan and Cilkscale
ifeq ($(CILKSAN),1)
	CFLAGS += -fsanitize=cilk
	LDFLAGS := $(COMMONFLAGS) -fuse-ld=lld -pthread --gcc-install-dir=/usr/lib/gcc/x86_64-linux-gnu/7 -fopencilk -fsanitize=cilk -ldl -lm
else ifeq ($(CILKSCALE),1)
	CFLAGS += -fcilktool=cilkscale
	LDFLAGS := $(COMMONFLAGS) -fuse-ld=lld -pthread --gcc-install-dir=/usr/lib/gcc/x86_64-linux-gnu/7 -fopencilk -fcilktool=cilkscale -ldl -lm
endif

ifeq ($(DEBUG),1)
	CFLAGS += -O0 -DDEBUG
else
	CFLAGS += -O3 -DNDEBUG
endif

ifeq ($(FLTO),1)
	CFLAGS += -flto
	LDFLAGS += -flto
endif

ifeq ($(VERBOSE),1)
	CFLAGS += -DDEBUG_VERBOSE=1
endif

# DO NOT MODIFY THE ARCHITECTURES
ifeq ($(ENGAGING),1)
	CFLAGS += -march=sandybridge
else ifeq ($(LOCAL),0)
	# You will be graded on haswell.
	CFLAGS += -march=haswell
else ifeq ($(UNAME),Darwin)
	CFLAGS += -DMACPORT
else
	CFLAGS += -march=native
endif

# First target is default
default: print_local_warning $(TARGET) ;

ifeq ($(LOCAL),0)
print_local_warning: ;
else
print_local_warning:
	@printf "\033[01;33mBE ADVISED: You have selected to build for your native architecture. This might be different than Haswell, which the AWS grading machines use.\033[00m\n"
	@printf "\033[01;33mUnless you have a good reason, unset the LOCAL flag or use LOCAL=0 before getting performance numbers on AWS.\033[00m\n"
endif

# Link the leiserchess binary
$(TARGET): $(OBJ)
	$(CC) $(LDFLAGS) $^ -o $@

%.o: %.c Makefile
	$(CC) $(CFLAGS) -MMD -c $< -o $@

-include $(DEP)

.PHONY: default format clean print_local_warning
clean:
	rm -f *.o *.d* *~ $(TARGET)

format:
	clang-format -i --style=file *.c *.h
