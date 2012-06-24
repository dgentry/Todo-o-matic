test:
	./todo.py
#	./runme.sh

install:
	cp todo-merge.py ~/bin/todo-merge
	cp todo-sweep.py ~/bin/todo-sweep

clean::
	rm -f *~ *# *.pyc
