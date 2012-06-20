#!/usr/bin/env python

def uniq(aList):
    """Eliminate duplicate items from a list.  The list need not be sorted."""
    result = []
    for item in aList:
        if not item in result:
            result.append(item)
        else:
            pass  #debug("Uniq'ed out %s" % str(item.__dict__))
    return result


if __name__ == "__main__":
    from dgtest import test
    #
    # Tests here
    #

    myList = ['a', 'b', 3, uniq, uniq, 'b']
    uniqueList = ['a', 'b', 3, uniq]

    test("Should remove duplicate items",
         uniq(myList) == uniqueList)

    test("Should not remove only instance of an item",
         'a' in uniq(myList))

    test("The empty list should stay empty",
         uniq([]) == [])
