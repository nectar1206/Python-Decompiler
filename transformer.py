#!/usr/bin/env python

import compiler
import sys

from pymeta.grammar import OMeta, OMetaGrammar

def strip_comments(s):
	"""Simple Python loop to strip out anything on a line after a #."""
	r = ''
	in_comment = False
	for character in s:
		if in_comment:
			if character == '\n':
				r = r + character
				in_comment = False
		else:
			if character == "#":
				in_comment = True
			else:
				r = r + character
	return r

def match_args(names, values, flag=0):
	if flag == "4":
		extra_args = names.pop()
	elif flag == "8":
		keyword_args = names.pop()
	elif flag == "12":
		keyword_args = names.pop()
		extra_args = names.pop()
	names.reverse()
	values.reverse()
	matched = []
	for i in range(len(names)):
		try:
			matched.append(names[i]+'='+values[i])
		except:
			matched.append(names[i])
	matched.reverse()
	if flag == "4":
		matched.append('*'+extra_args)
	elif flag == "8":
		matched.append('**'+keyword_args)
	elif flag == "12":
		matched.append('*'+extra_args)
		matched.append('**'+keyword_args)
	out = ', '.join(matched)
	return out

def from_flag(flag, module):
	if flag == '0':
		return module
	elif flag == '2':
		return '..'+module
	else:
		return 'UNKNOWN "FROM" FLAG: '+flag

gram = """
# This grammar matches against the ASTs produced by Python 2.x's
# compiler module. It produces Python code to match the AST.

# The parameter "i" given to most rules is the desired level of
# indentation for the generated code. The number used in the rule "any"
# is sufficient to indent the whole output, since it is subsequently
# passed to every other rule.

# "any" is the entry point into the AST. It matches any number of AST
# nodes and outputs the generated code. The number given to the "things"
# is the initial amount of indentation to use in the output.

any ::= <thing 0>*:t													=> ''.join(t)

# A "thing" is anything of interest. It will match anything, since it
# includes a trivial match at the bottom. The trick here is in the
# ordering. Strings are first, since they can contain any text whilst
# still remaining just data. Nodes follow, then data structures, and
# finally a trivial match.

# "string" matches anything in quotes, and outputs that including the
# quotes (to get an output without the quotes used "quoted")
thing :i ::= <string i>:s												=> s

           ## The following are AST nodes

           #
           | <del i>:d													=> d

           # "add" is addition
           | <add i>:a													=> '('+a+')'

           # "and" matches an and operation
           | <and i>:a													=> a

           # "assattr" matches attribute binding
           | <assattr i>:a

           # "assname" is the binding of a value to a variable name
           | <assname i>:a												=> a

           # "asstuple" is the binding of members of one tuple to another
           | <asstuple i>:a												=> a

           # "assert" is an assertion (mainly used for debugging)
           | <assert i>:a												=> a

           # "assign" is the binding of a value to something
           | <assign i>:a												=> a

           # "augassign" matches an increment, decrement, etc.
           | <augassign i>:a											=> a

           #
           | <backquote i>:b											=> b

           #
           | <bitand i>:b												=> b

           #
           | <bitor i>:b												=> b

           #
           | <bitxor i>:b												=> b

           #
           | <break i>:b												=> b

           # "callfunc" is a function call, complete with arguments
           | <callfunc i>:c												=> c

           # "class" is a Python class
           | <class i>:c												=> c

           # "compare" matches tests for (in)equality
           | <compare i>:c												=> c

           # "const" is a constant value
           | <const i>:c												=> c

           #
           | <continue i>:c												=> c

           #
           | <decorators i>:d											=> d

           # "dict" matches a Python dictionary datastructure
           | <dict i>:d													=> d

           # "discard" wraps commands the return values of which are not
           # used anywhere else in the program
           | <discard i>:d												=> d

           # "div" is division
           | <div i>:d													=> '('+d+')'

           #
           | <ellipsis i>:e												=> e

           #
           | <expression i>:e											=> e

           #
           | <exec i>:e													=> e

           #
           | <floordiv i>:f												=> f

           # "for" matches a for loop
           | <for i>:f													=> f

           # "from" imports specified things from one module into the
           # current namespace, renaming them if instructed to
           | <from i>:f													=> f

           # "function" is a function definition, complete with code and
           # arguments
           | <function i>:f												=> f

           #
           | <genexpr i>:g												=> g

           #
           | <genexprfor i>:g											=> g

           #
           | <genexprif i>:g											=> g

           #
           | <genexprinner i>:g											=> g

           # "getattr" gets a value from some namespace (for example a
           # property of an object)
           | <getattr i>:a												=> a

           #
           | <global i>:g												=> g

           # "if" matches if statements
           | <if i>:f													=> f

           # "import" imports modules into the current namespace, and
           # possibly renames them if instructed to
           | <import i>:m												=> m

           #
           | <keyword i>:k												=> k

           #
           | <lambda i>:l												=> l

           #
           | <leftshift i>:l											=> l

           # "listnode" is a list in the original code (not to be
           # confused with "list" which is a series of values in square
           # brackets)
           | <listnode i>:l												=> l

           #
           | <listcomp i>:l												=> l

           #
           | <listcompfor i>:l											=> l

           #
           | <listcompif i>:l											=> l

           #
           | <mod i>:m													=> '('+m+')'

           # "module" is a Python module, ie. a file of Python code
           | <module i>:m												=> m

           # "mul" is multiplication
           | <mul i>:m													=> '('+m+')'

           # "name" calls a variable
           | <name i>:n													=> n

           # "not" matches a not operation
           | <not i>:n													=> n

           # "or" matches an or operation
           | <or i>:o													=> o

           # "pass" matches a pass statement
           | <pass i>:p													=> p

           # "power" is exponentiation
           | <power i>:p												=> '('+p+')'

           # "print" is a print statement followed by a comma, which
           # prevents the buffer from flushing and doesn't end in a new
           # line
           | <print i>:p												=> p

           # "printnl" is a normal print statement, ending the line and
           # flushing the output buffer
           | <printnl i>:p												=> p

           #
           | <raise i>:r												=> r

           # "return" is a return statement
           | <return i>:r												=> r

           #
           | <rightshift i>:r											=> r

           #
           | <slice i>:s												=> s

           #
           | <sliceobj i>:s												=> s

           # "stmt" is a statement, ie. a list of commands
           | <stmt i>:s													=> s

           # "sub" is subtraction
           | <sub i>:s													=> '('+s+')'

           # "subscript" matches object indexing (such as "mylist[2]")
           | <subscript i>:s											=> s

           # "tryexcept" matches "try" statements and their accompanying
           # "except" and "else" statements
           | <tryexcept i>:t											=> t

           #
           | <tryfinally i>:t											=> t

           # "tuplenode" is a tuple in the original code (not to be
           # confused with "tuple" which is a series of values in
           # brackets)
           | <tuplenode i>:t											=> t

           #
           | <unaryadd i>:u												=> u

           # "unarysub" negates a value (eg. unary sub of 1 is -1)
           | <unarysub i>:u												=> u

           # "while" matches a while loop
           | <while i>:w												=> w

           #
           | <with i>:w													=> w

           #
           | <yield i>:y												=> y

           ## The following are common data formats found in the AST

           # "sep" is a comma followed by a space, used as a separator
           # in tuples and lists
           | <sep i>:s													=> ''

           # "tuple" matches a series of comma-separated values in
           # brackets. Not to be confused with "tuplenode" which matches
           # a Python tuple datastructure
           | <tuple i>:t												=> t

           # "list" matches a series of comma-separated values in square
           # brackets. Not to be confused with "listnode" which matches
           # a Python list datastructure
           | <list i>:l													=> l

           # "none" matches Python's null value. Note that this
           # is simply the text "None", and thus should be used
           # carefully around things like strings, which could contain
           # those four characters
           | <none i>:n													=> n

           # "num" matches a number, positive or negative, integer or
           # fractional, real or complex, indexed or not
           | <num>:n													=> n

           # This catches anything else that occurs in the stream if it
           # doesn't match something above. It consumes 1 character at a
           # time
           | <anything>:a												=> a


## The following match the AST nodes of the compiler module

#Add((Power((CallFunc(Getattr(Name('math'), 'hypot'), [Sub((Subscript(Name('point_position'), 'OP_APPLY', [Const(0)]), Subscript(Name('position'), 'OP_APPLY', [Const(0)]))), Sub((Subscript(Name('point_position'), 'OP_APPLY', [Const(1)]), Subscript(Name('position'), 'OP_APPLY', [Const(1)])))], None, None), Const(2))), Const(9.9999999999999995e-07)))
# Matches addition
add :i ::= <token 'Add'> <addcontents i>:a								=> a

addcontents :i ::= <token '(('> <thing i>:left <sep i>
                                <thing i>:right <token '))'>			=> left + ' + ' + right


# Matches an and operator
and :i ::= <token 'And(['> <andcontents i>:a <token ')'>				=> a

andcontents :i ::= <token ']'>											=> ''
                 | <sep i> <andcontents i>:a							=> ' and '+a
                 | <thing i>:t <andcontents i>:a						=> '('+t+')'+a


# Matches the assignment of an attribute
assattr :i ::= <token 'AssAttr('> <thing i>:l <sep i> <quoted i>:a
               <sep i> <quoted i> <token ')'>							=> l+'.'+a


# Matches binding a value to a variable name
assname :i ::= <token 'AssName'> <assnamecontents i>:a					=> a

assnamecontents :i ::= <token '('> <quoted i>:name <sep i>
                                   <token "'OP_ASSIGN'"> <token ')'>	=> name


# Matches binding multiple values at once
asstuple :i ::= <token 'AssTuple(['> <asstuplecontents i>:a <token ')'>	=> '('+a+')'

asstuplecontents :i ::= <token ']'>										=> ''
                      | <sep i> <asstuplecontents i>:l					=> ', '+l
                      | <thing i>:t <asstuplecontents i>:l				=> t+l

#Assert(Compare(Name('stuff'), [('is not', Name('None'))]), Mod((Const("Couldn't find the module '%s'"), Tuple([Name('base_name')]))))
# Matches an assertion
assert :i ::= <token 'Assert('> <thing i>:t <sep i>
                                <none i> <token ')'>					=> 'assert '+t
            | <token 'Assert('> <thing i>:t <sep i> <thing i>:m
              <token ')'>												=> 'assert '+t+', '+m


# Matches a value binding
assign :i ::= <token 'Assign(['> <assignleft i>:l <sep i>
                                 <assignright i>:r <token ')'>			=> l+r

assignleft :i ::= <token ']'>											=> ''
                | <sep i> <assignleft i>:l								=> l
                | <thing i>:t <assignleft i>:l							=> t+' = '+l

assignright :i ::= <thing i>:t											=> t


# Matches a combined operation and assign, such as "+=" or "/="
augassign :i ::= <token 'AugAssign('> <thing i>:l <sep i>
                                      <quoted i>:o <sep i>
                                      <thing i>:r <token ')'>			=> l+' '+o+' '+r


#																		####################################
backquote :i ::= ' '


#																		#####################################
bitand :i ::= ' '


#																		####################################
bitor :i ::= ' '


#																		###############################
bitxor :i ::= ' '


# Matches a break (leaving a loop before the conditions specify it)
break :i ::= <token 'Break()'>											=> 'break'


# Matches a function call
callfunc :i ::= <token 'CallFunc('> <thing i>:name <sep i> <token '['>
                <callfunccontents i>:c									=> name+'('+c

                      # Catch empty arguments first
callfunccontents :i ::= <token ']'> <sep i> <none i> <sep i> <none i>
                        <token ')'>										=> ')'
                      # Now catch either an argument lists or a dictionary
                      | <token ']'> <sep i> <thing i>:list <sep i>
                        <none i> <token ')'>							=> '*'+list+')'
                      | <token ']'> <sep i> <none i> <sep i>
                        <thing i>:kw <token ')'>						=> '**'+kw+')'
                      # Now catch both (since "None" is a "thing" we need to catch empty args with the above 3)
                      | <token ']'> <sep i> <thing i>:list <sep i>
                        <thing i>:kw <token ')'>						=> '*'+list+', **'+kw+')'
                      # Now do the same, but including regular arguments, starting with no list or dictionary
                      | <callfuncargs i>:a <sep i>
                        <none i>:list <sep i> <none i>:kw <token ')'>	=> a+')'
                      # Now catch arguments plus a list or dictionary
                      | <callfuncargs i>:a <sep i>
                        <thing i>:list <sep i> <none i>:kw <token ')'>	=> a+', *'+list+')'
                      | <callfuncargs i>:a <sep i> <none i>:list
                        <sep i> <thing i>:kw <token ')'>				=> a+', **'+kw+')'
                      # Finally catch all three
                      | <callfuncargs i>:a <sep i> <thing i>:list
                        <sep i> <thing i>:kw <token ')'>				=> a+', *'+list+', **'+kw+')'

callfuncargs :i ::= <token ']'>											=> ''
                  | <sep i> <callfuncargs i>:a							=> ', '+a
                  | <thing i>:t <callfuncargs i>:a						=> t+a


# Matches a Python class
class :i ::= <token 'Class('> <quoted i>:n <sep i> <token '['>
             <classcontents i>:c <sep i> <none i> <sep i> <stmt i+1>:s
             <token ')'>												=> 'class '+n+'('+c+\"""):\n\"""+s
           | <token 'Class('> <quoted i>:n <sep i> <token '['>
             <classcontents i>:c <sep i> <string i>:d <sep i>
             <stmt i+1>:s <token ')'>									=> 'class '+n+'('+c+\"""):\n\"""+(i+1)*'\t'+d+\"""\n\"""+s

classcontents :i ::= <token ']'>										=> ''
                   | <sep i> <classcontents i>:c						=> ', '+c
                   | <thing i>:t <classcontents i>:c					=> t+c


# Matches comparisons
compare :i ::= <token 'Compare('> <thing i>:l <sep i>
               <token '['> <comparecontents i>:r <token ')'>			=> '('+l+') '+r

comparecontents :i ::= <token ']'>										=> ''
                     | <sep i> <comparecontents i>:r					=> r
                     | <token '('> <quoted i>:c <sep i> <thing i>:r
                       <token ')'> <comparecontents i>:e				=> c+' ('+r+') '+e


# Matches constants
const :i ::= <token 'Const('> <none i> <token ')'>						=> ''
           | <token 'Const('> <thing i>:c <token ')'>					=> c


# Matches continue (skipping of loop iteration)
continue :i ::= <token 'Continue()'>									=> 'continue'


# Matches functions used to modify the behaviour of code
decorators :i ::= <token 'Decorators(['> <thing i>:dec <token '])'>		=> '@'+dec
                | <token 'Decorators('> <list i>:decs <token ')'>		=> '@'+(\"""\n\"""+('\t'*i)+'@').join(decs)

#Module(None, Stmt([
#AssName('x', 'OP_DELETE'),
#AssName('y', 'OP_DELETE'),
#AssTuple([AssName('a', 'OP_DELETE'), AssName('b', 'OP_DELETE'), AssName('c', 'OP_DELETE')]),
#Subscript(Name('x'), 'OP_DELETE', [Name('a')]),
#Slice(Name('x'), 'OP_DELETE', Name('a'), Name('b')), Subscript(Name('x'), 'OP_DELETE', [Sliceobj([Name('a'), Name('b'), Name('c')])])]))
# Matches deletions
del :i ::= <delcontents i>:c											=> 'del '+c

delcontents :i ::= <deltuple i>:t										=> t
                 | <delname i>:n										=> n
                 | <delsub i>:s											=> s
                 | <delslice i>:s										=> s
                 | <delattr i>:a										=> a

delname :i ::= <token 'AssName('> <delnamecontents i>:a					=> a

delnamecontents :i ::= <quoted i>:name <sep i>
                       <token "'OP_DELETE'"> <token ')'>				=> name

deltuple :i ::= <token 'AssTuple(['> <deltuplecontents i>:a <token ')'>	=> a

deltuplecontents :i ::= <token ']'>										=> ''
                      | <sep i> <deltuplecontents i>:l					=> ', '+l
                      | <delcontents i>:t <deltuplecontents i>:l		=> t+l

delsub :i ::= <token 'Subscript('> <thing i>:l <sep i>
                 <token "'OP_DELETE'"> <sep i>
                 <token '['> <thing i>:s <token '])'>					=> l+'['+s+']'

delslice :i ::= <token 'Slice('> <thing i>:t <sep i> <token "'OP_DELETE'">
                <sep i> <none i> <sep i> <none i> <token ')'>			=> t+'[:]'
           | <token 'Slice('> <thing i>:t <sep i> <token "'OP_DELETE'">
             <sep i> <none i> <sep i> <thing i>:r <token ')'>			=> t+'[:'+r+']'
           | <token 'Slice('> <thing i>:t <sep i> <token "'OP_DELETE'">
             <sep i> <thing i>:l <sep i> <none i> <token ')'>			=> t+'['+l+':]'
           | <token 'Slice('> <thing i>:t <sep i> <token "'OP_DELETE'">
             <sep i> <thing i>:l <sep i> <thing i>:r <token ')'>		=> t+'['+l+':'+r+']'

delattr :i ::= <token 'AssAttr('> <thing i>:l <sep i>
               <quoted i>:a <sep i> <token "'OP_DELETE'"> <token ')'>	=> l+'.'+a


# Matches a dictionary datastructure
dict :i ::= <token 'Dict(())'>											=> '{}'
          | <token 'Dict(['> <dictcontents i>:d <token ')'>				=> '{'+d+'}'

dictcontents :i ::= <token ']'>											=> ''
                  | <sep i> <dictcontents i>:d							=> ', '+d
                  | <token '('> <thing i>:k <sep i>
                                <thing i>:v <token ')'>
                                <dictcontents i>:d						=> k+':'+v+d


# Matches possibly redundant commands
discard :i ::= <token 'Discard('> <thing i>:t <token ')'>				=> t


# Matches division
div :i ::= <token 'Div'> <divcontents i>:d								=> d

divcontents :i ::= <token '(('> <thing i>:left <sep i>
                                <thing i>:right <token '))'>			=> left + ' / ' + right


#																		###################################
ellipsis :i ::= ' '


#																		##################################
expression :i ::= ' '


# Matches execution of strings containing code
exec :i ::= <token 'Exec('> <thing i>:c <sep i> <none i> <sep i>
            <none i> <token ')'>										=> 'exec('+c+')'


#																		###################################
floordiv :i ::= ' '


# Matches for loops
for :i ::= <token 'For('> <assname i>:a <sep i> <thing i>:c <sep i>
                          <stmt i+1>:s <sep i> <none i> <token ')'>		=> 'for '+a+' in '+c+\""":\n\"""+s
         | <token 'For('> <assname i>:a <sep i> <thing i>:c <sep i>
                          <stmt i+1>:s <sep i> <stmt i+1>:e <token ')'>	=> 'for '+a+' in '+c+\""":\n\"""+s+\"""\n\"""+(i*'\t')+\"""else:\n\"""+e
         | <token 'For('> <asstuple i>:a <sep i> <thing i>:c <sep i>
                          <stmt i+1>:s <sep i> <none i> <token ')'>		=> 'for '+a+' in '+c+\""":\n\"""+s
         | <token 'For('> <asstuple i>:a <sep i> <thing i>:c <sep i>
                          <stmt i+1>:s <sep i> <stmt i+1>:e <token ')'>	=> 'for '+a+' in '+c+\""":\n\"""+s+\"""\n\"""+(i*'\t')+\"""else:\n\"""+e


# Matches namespace injections
from :i ::= <token 'From('> <quoted i>:m <sep i> <token '['>
            <fromcontents i>:c <sep i> <thing i>:f <token ')'>			=> 'from '+from_flag(f,m)+' import '+c

fromcontents :i ::= <token ']'>											=> ''
                  | <token '('> <quoted i>:m <sep i>
                    <none i> <token ')'> <fromcontents i>:c				=> m+c
                  | <token '('> <quoted i>:m <sep i>
                    <quoted i>:n <token ')'> <fromcontents i>:c			=> m+' as '+n+c
                  | <sep i> <fromcontents i>:c							=> ', '+c


# Matches a Python function definition
function :i ::= <token 'Function('>
                <functiondecorators i>:decs <sep i>
                <quoted i>:n <sep i> <token '['>
                <functioncontents i>:a <sep i> <token '['>
                <functioncontents i>:v <sep i> <thing i>:f <sep i>
                <none i> <sep i>
                <stmt i+1>:s <token ')'>								=> decs+\"""\n\"""+('\t'*i)+'def '+n+'('+match_args(a,v,flag=f)+\"""):\n\"""+s
              | <token 'Function('> <functiondecorators i>:decs <sep i>
                <quoted i>:n <sep i> <token '()'> <sep i> <token '()'>
                <sep i> <thing i>:f <sep i> <none i> <sep i>
                <stmt i+1>:s <token ')'>								=> decs+'def '+n+\"""():\n\"""+s
              | <token 'Function('>
                <functiondecorators i>:decs <sep i>
                <quoted i>:n <sep i> <token '['>
                <functioncontents i>:a <sep i> <token '['>
                <functioncontents i>:v <sep i> <thing i>:f <sep i>
                <string i>:d <sep i>
                <stmt i+1>:s <token ')'>								=> decs+'def '+n+'('+match_args(a,v,flag=f)+\"""):\n\"""+((i+1)*'\t')+d+\"""\n\"""+s
              | <token 'Function('> <functiondecorators i> <sep i>
                <quoted i>:n <sep i> <token '()'> <sep i> <token '()'>
                <sep i> <thing i>:f <sep i> <string i>:d <sep i>
                <stmt i+1>:s <token ')'>								=> decs+'def '+n+\"""():\n\"""+((i+1)*'\t')+d+\"""\n\"""+s

functiondecorators :i ::= <decorators i>:decorators						=> decorators + \"""\n\"""+('\t'*i)
                        | <none i>										=> ''

functioncontents :i ::= <token ']'>										=> []
                      | <arg i>:t <token ']'>							=> [t]
                      | (<argsep i>)*:xs <arg i>:x <token ']'>			=> xs + [x]

argsep :i ::= <arg i>:a <sep i>											=> a

arg :i ::= <quoted i>:q													=> q
         | <token '('> (<argsep i>)*:xs <arg i>:x <token ')'>			=> '('+', '.join(xs)+', '+x+')'
         | <thing i>:t													=> t


# A list-generating expression
genexpr :i ::= <token 'GenExpr('> <thing i>:inner <token ')'>			=> '('+inner+')'


# The source in a list-generating expression
genexprfor :i ::= <token 'GenExprFor('> <thing i>:name <sep i>
                  <thing i>:list <sep i> <token '['>
                  <genexprforcontents i>:ifs <token ')'>				=> ' for '+name+' in '+list+ifs

genexprforcontents :i ::= <token ']'>									=> ''
                        | <thing i>:thing <genexprforcontents i>:rest	=> thing+rest


# Matches conditions on a list-generating expression
genexprif :i ::= <token 'GenExprIf('> <thing i>:condition <token ')'>	=> ' if '+condition


# The body of a list-generating expression
genexprinner :i ::= <token 'GenExprInner('> <thing i>:left <sep i>
                    <token '['> <genexprinnercontents i>:right
                    <token ')'>											=> left + ' ' + right

genexprinnercontents :i ::= <token ']'>									=> ''
                          | <thing i>:thing <genexprinnercontents i>:r	=> thing + r


# Matches attribute lookup
getattr :i ::= <token 'Getattr('> <thing i>:o <sep i>
                                  <quoted i>:a <token ')'>				=> o+'.'+a


# Matches injection of global variables
global :i ::= <token 'Global(['> <globalcontents i>:g <token ')'>		=> 'global '+g

globalcontents :i ::= <token ']'>										=> ''
                    | <sep i> <globalcontents i>:g						=> ', '+g
                    | <quoted i>:q <globalcontents i>:g					=> q+g
                    | <thing i>:t <globalcontents i>:g					=> t+g


# Matches an if statement
if :i ::= <token 'If([('> <thing i>:c <sep i>
                         <stmt i+1>:s <token ')'> <sep i>
                         <elifs i>:e <sep i> <else i>:x <token ')'>		=> "if "+c+\""":\n\"""+s+\"""\n\"""+e+\"""\n\"""+'\t'*i+x
        | <token 'If([('> <thing i>:c <sep i>
                          <stmt i+1>:s <token ')]'> <sep i> <else i>:x
                          <token ')'>									=> "if "+c+\""":\n\"""+s+\"""\n\"""+'\t'*i+x

elifs :i ::= <token ']'>												=> ''
           | <sep i> <elifs i>:e										=> e
           | <token '('> <thing i>:c <sep i>
                         <stmt i+1>:s <token ')'> <elifs i>:x			=> '\t'*i+"elif "+c+\""":\n\"""+s+x

else :i ::= <none i>													=> ''
          | <stmt i+1>:s												=> \"""else:\n\"""+s

#Import([('compiler', None), ('traceback', None)])
# Matches module imports
import :i ::= <token 'Import(['> <importcontents i>:c <token ')'>		=> 'import '+c

importcontents :i ::= <token ']'>										=> ''
                    | <sep i> <importcontents i>:c						=> ', '+c
                    | <token '('> <quoted i>:m <sep i>
                      <none i> <token ')'> <importcontents i>:c			=> m+c
                    | <token '('> <quoted i>:m <sep i>
                      <quoted i>:n <token ')'> <importcontents i>:c		=> m+' as '+n+c


# Matches key=value arguments to functions
keyword :i ::= <token 'Keyword('> <quoted i>:k <sep i> <thing i>:t
               <token ')'>												=> k+'='+t


# Matches stateless function definition
lambda :i ::= <token 'Lambda(['> <functioncontents i>:n <sep i>
              <token '['> <functioncontents i>:v <sep i> <thing i>
              <sep i> <thing i>:code <token ')'>						=> 'lambda '+match_args(n,v)+': '+code
            | <token 'Lambda((), (), '> <thing i> <sep i> <thing i>:code
              <token ')'>												=> 'lambda: '+code


#																		##########################
leftshift :i ::= ' '


# Matches a list datastructure
listnode :i ::= <token 'List(['> <listnodecontents i>:l <token ')'>		=> '['+l[:-2]+']'
              | <token 'List(())'>										=> '[]'

listnodecontents :i ::= ']'												=> ''
                      | <sep i> <listnodecontents i>:l					=> l
                      | <thing i>:t <listnodecontents i>:l				=> t+', '+l


# Matches list comprehensions
listcomp :i ::= <token 'ListComp('> <thing i>:l <sep i> <token '['>
                <listcompcontents i>:c <token ')'>						=> '['+l+' '+c+']'

listcompcontents :i ::= <token ']'>										=> ''
                      | <thing i>:t <listcompcontents i>:l				=> t+l


# Matches list comprehension based on a for loop
listcompfor :i ::= <token 'ListCompFor('> <thing i>:n <sep i>
                   <thing i>:l <sep i> <token '['>
                   <listcompforcontents i>:c <token ')'>				=> 'for '+n+' in '+l+' '+c

listcompforcontents :i ::= <token ']'>									=> ''
                         | <thing i>:t <listcompforcontents i>:l		=> t+l


# Matches if conditions to list comprehensions
listcompif :i ::= <token 'ListCompIf('> <thing i>:condition <token ')'>	=> ' if '+condition


# Matches modulo (remainder) operations
mod :i ::= <token 'Mod(('> <thing i>:l <sep i> <thing i>:r <token '))'>	=> l+' % '+r


# Matches a Python module and its contents
module :i ::= <token 'Module'> <modcontents i>:t						=> t

modcontents :i ::= <token '('> <none i> <sep i> <tupleval i>:t			=> t
                 | <token '('> <string i>:d <sep i> <tupleval i>:t		=> d + \"""\n\""" + t


# Matches multiplication
mul :i ::= <token 'Mul'> <mulcontents i>:m								=> m

mulcontents :i ::= <token '(('> <thing i>:left <sep i>
                                <thing i>:right <token '))'>			=> left + ' * ' + right


# Matches a variable name
name :i ::= <token 'Name'> <namecontents i>:n							=> n

namecontents :i ::= <token '('> <quoted i>:n <token ')'>				=> n


# Matches a not operation
not :i ::= <token 'Not('> <thing i>:t <token ')'>						=> 'not ('+t+')'


# Matches an or operator
or :i ::= <token 'Or(['> <orcontents i>:o <token ')'>					=> o

orcontents :i ::= <token ']'>											=> ''
                | <sep i> <orcontents i>:o								=> ' or '+o
                | <thing i>:t <orcontents i>:o							=> '('+t+')'+o


# Matches a pass statement
pass :i ::= <token 'Pass()'>											=> 'pass'


# Matches exponentiation
power :i ::= <token 'Power(('> <thing i>:o <sep i>
                              <thing i>:p <token '))'>					=> o+'**'+p


# Matches print with no newline
print :i ::= <token 'Print(['> <thing i>:p <token ']'> <sep i>
                               <none i> <token ')'>						=> 'print '+p+','
           | <token 'Print(['> <thing i>:p <token ']'> <sep i>
                               <printout i>:out <token ')'>				=> 'print >> '+out+', '+p+','
           | <token 'Print(['> <printcontents i>:p <sep i>
                               <none i> <token ')'>						=> 'print '+p+','
           | <token 'Print(['> <printcontents i>:p <sep i>
                               <printout i>:out <token ')'>				=> 'print >> '+out+', '+p+','

printcontents :i ::= <token ']'>										=> ''
                   | <string i>:s <printcontents i>:p					=> s+p
                   | <sep i> <printcontents i>:p						=> ', '+p
                   | <thing i>:t <printcontents i>:p					=> t+p

printout :i ::= <none i>												=> ''
              | <thing i>:t												=> t


# Matches print
printnl :i ::= <token 'Printnl([], '> <none i> <token ')'>				=> 'print'
             | <token 'Printnl(['> <thing i>:p <token ']'> <sep i>
               <none i> <token ')'>										=> 'print '+p
             | <token 'Printnl(['> <thing i>:p <token ']'> <sep i>
               <printout i>:o <token ')'>								=> 'print >> '+o+', '+p
             | <token 'Printnl(['> <printcontents i>:p <sep i>
               <none i> <token ')'>										=> 'print '+p
             | <token 'Printnl(['> <printcontents i>:p <sep i>
               <printout i>:o <token ')'>								=> 'print >> '+o+', '+p


# Matches exception raising
raise :i ::= <token 'Raise('> <none i> <sep i> <none i> <sep i> <none i>
             <token ')'>												=> 'raise'
           | <token 'Raise('> <thing i>:t <sep i> <none i> <sep i>
                              <none i> <token ')'>						=> 'raise '+t
           | <token 'Raise('> <thing i>:t <sep i> <thing i>:a <sep i>
                              <none i> <token ')'>						=> 'raise '+t+', '+a
           | <token 'Raise('> <thing i>:t <sep i> <thing i>:a <sep i>
                              <thing i>:b <token ')'>					=> 'raise '+t+', '+a+', '+b


# Matches return statements
return :i ::= <token 'Return('> <thing i>:t <token ')'>					=> 'return '+t


#																		#########################
rightshift :i ::= ' '


# Matches slicing of iterables (eg. x[5:15])
slice :i ::= <token 'Slice('> <thing i>:t <sep i> <quoted i> <sep i>
             <none i> <sep i> <none i> <token ')'>						=> t+'[:]'
           | <token 'Slice('> <thing i>:t <sep i> <quoted i> <sep i>
             <none i> <sep i> <thing i>:r <token ')'>					=> t+'[:'+r+']'
           | <token 'Slice('> <thing i>:t <sep i> <quoted i> <sep i>
             <thing i>:l <sep i> <none i> <token ')'>					=> t+'['+l+':]'
           | <token 'Slice('> <thing i>:t <sep i> <quoted i> <sep i>
             <thing i>:l <sep i> <thing i>:r <token ')'>				=> t+'['+l+':'+r+']'


# Matches more advanced iterator slicing (eg. x[start:end:step])
sliceobj :i ::= <token 'Sliceobj(['> <sliceobjcontents i>:s <token ')'>	=> s

sliceobjcontents :i ::= <token ']'>										=> ''
                      | <sep i> <sliceobjcontents i>:s					=> ':'+s
                      | <thing i>:t <sliceobjcontents i>:s				=> t+s


# Matches a series of Python commands
stmt :i ::= <token 'Stmt'> <stmtcontents i>:s							=> s

stmtcontents :i ::= <token '(['> <stmtlines i>:s <token ')'>			=> s

stmtlines :i ::= <token ']'>											=> ''
               | <thing i>:t <stmtlines i>:s							=> i*'\t' + t + \"""\n\""" + s


# Matches subtraction
sub :i ::= <token 'Sub'> <subcontents i>:s								=> s

subcontents :i ::= <token '(('> <thing i>:left <sep i>
                                <thing i>:right <token '))'>			=> left + ' - ' + right


# Matches indexing of an object (eg. mylist[5])
subscript :i ::= <token 'Subscript('> <thing i>:l <sep i>
                 <token "'OP_APPLY'"> <sep i>
                 <token '['> <thing i>:s <token '])'>					=> l+'['+s+']'
               | <token 'Subscript('> <thing i>:l <sep i>
                 <token "'OP_ASSIGN'"> <sep i>
                 <token '['> <thing i>:s <token '])'>					=> l+'['+s+']'
               | <token 'Subscript('> <thing i>:l <sep i>
                 <quoted i> <sep i>
                 <token '['> <thing i>:s <token '])'>					=> l+'['+s+']'

#TryExcept(Stmt([Printnl([Const('x')], None)]), [(Name('SyntaxError'), None, Stmt([Pass()])), (Name('ParseError'), None, Stmt([Printnl([Const('y')], None)])), (None, None, Stmt([Printnl([Const('z')], None)]))], None)
# Matches "try:" "except:" statements
tryexcept :i ::= <token 'TryExcept('> <stmt i+1>:t <sep i> <token '['>
                 <trycontents i>:e <sep i> <none i> <token ')'>			=> \"""try:\n\"""+t+e
               | <token 'TryExcept('> <stmt i+1>:t <sep i> <token '['>
                 <trycontents i>:e <sep i> <stmt i+1>:s <token ')'>		=> \"""try:\n\"""+t+e+\"""\n\"""+(i*'\t')+\"""else:\n\"""+s

trycontents :i ::= <token ']'>											=> ''
                 | <sep i> <trycontents i>:t							=> t
                 | <token '('> <none i> <sep i> <none i> <sep i>
                   <stmt i+1>:e <token ')'> <trycontents i>:c			=> '\t'*i+\"""except:\n\"""+e+c
                 | <token '('> <thing i>:x <sep i> <none i>:y <sep i>
                   <stmt i+1>:e <token ')'> <trycontents i>:c			=> '\t'*i+'except '+x+\""":\n\"""+e+c
                 | <token '('> <thing i>:x <sep i> <thing i>:y <sep i>
                   <stmt i+1>:e <token ')'> <trycontents i>:c			=> '\t'*i+'except '+x+', '+y+\""":\n\"""+e+c

#TryFinally(<Stmt><sep> Stmt())
# Matches "finally" statements ("do this regardless") after a try/except
tryfinally :i ::= <token 'TryFinally('> <tryexcept i>:t <sep i>
                                        <stmt i+1>:s <token ')'>		=> t + \"""\n\""" + '\t'*i + \"""finally:\n\""" + s
                | <token 'TryFinally('> <stmt i+1>:s1 <sep i>
                  <stmt i+1>:s2 <token ')'>								=> \"""try:\n\"""+s1+\"""\n\"""+('\t'*i)+\"""finally:\n\"""+s2


# Matches a tuple datastructure
tuplenode :i ::= <token 'Tuple(['> <thing i>:singleton <token '])'>		=> '('+singleton+',)'
               | <token 'Tuple(['> <tuplenodecontents i>:t ')'			=> '('+t+')'
               | <token 'Tuple(())'>									=> '()'

tuplenodecontents :i ::= ']'											=> ''
                       | <sep i> <tuplenodecontents i>:t				=> ', '+t
                       | <thing i>:t <tuplenodecontents i>:c			=> t+c


# Matches explicitly positive values
unaryadd :i ::= <token 'UnaryAdd('> <thing i>:t <token ')'>				=> '+'+t


# Matches negative values
unarysub :i ::= <token 'UnarySub('> <thing i>:t <token ')'>				=> '-'+t


# Matches while loops
while :i ::= <token 'While('> <thing i>:t <sep i>
                              <stmt i+1>:s <sep i>
                              <thing i> <token ')'>						=> 'while '+t+\""":\n\"""+s


#																		#######################
with :i ::= ' '


# Matches 'yield' statements
yield :i ::= <token 'Yield('> <thing i>:t <token ')'>					=> 'yield '+t


## The following match common value formats used in the above

# Matches numbers

dig ::= '0'																=> '0'
      | '1'																=> '1'
      | '2'																=> '2'
      | '3'																=> '3'
      | '4'																=> '4'
      | '5'																=> '5'
      | '6'																=> '6'
      | '7'																=> '7'
      | '8'																=> '8'
      | '9'																=> '9'

whole ::= <dig>+:digits												=> ''.join(digits)

fraction ::= <whole>:whole '.' <whole>:fraction							=> whole + '.' + fraction

int ::= <whole>:w '.'													=> w+'.'
      | <whole>:w														=> w

vals ::= <fraction>:f													=> f
       | <int>:i														=> i

posneg ::= '-' <vals>:value												=> '-'+value
         | <vals>:value

exp ::= <posneg>:value 'e' <posneg>:exponent							=> value+'e'+exponent
      | <posneg>:value													=> value

complex ::= <exp>:number 'j'											=> number+'j'
          | <exp>:number												=> number

num ::= <complex>:number												=> number

# Matches comma separation and outputs it
sep :i ::= <token ', '>													=> ', '


# Matches a value in quotes, returning the value with no quotes
# (also see "string")
quoted :i ::= <token 'u'> <quote i>:q									=> q
            | <quote i>:q												=> q

quote :i ::= <token "'''"> <quotetriplesingle i>:q						=> q
            | <token '""'> '"' <quotetripledouble i>:q					=> q
            | <token "'"> <quotesingle i>:q								=> q
            | <token '"'> <quotedouble i>:q								=> q

quotesingle :i ::= "'"													=> ''
                 | <anything>:a <quotesingle i>:q						=> a+q

quotedouble :i ::= '"'													=> ''
                 | <anything>:a <quotedouble i>:q						=> a+q

quotetriplesingle :i ::= "'" "'" "'"									=> ''
                       | <anything>:a <quotetriplesingle i>:q			=> a+q

quotetripledouble :i ::= '"' '"' '"'									=> ''
                       | <anything>:a <quotetripledouble i>:q			=> a+q


# Matches a value in quotes, returning the value and the quotes. For
# a rule which doesn't return the quotes see "quoted"
string :i ::= <token 'u'> <str i>:s										=> 'u'+s
            | <str i>:s													=> s

str :i ::= <token "'''"> <stringtriplesingle i>:q					=> "'''"+q+"'''"
            | <token '""'> '"' <stringtripledouble i>:q					=> '""'+'"'+q+'""'+'"'
            | <token "'"> <stringsingle i>:q							=> "'"+q+"'"
            | <token '"'> <stringdouble i>:q							=> '"'+q+'"'

stringsingle :i ::= "'"													=> ''
                 | <anything>:a <stringsingle i>:q						=> a+q

stringdouble :i ::= '"'													=> ''
                 | <anything>:a <stringdouble i>:q						=> a+q

stringtriplesingle :i ::= "'" "'" "'"									=> ''
                       | <anything>:a <stringtriplesingle i>:q			=> a+q

stringtripledouble :i ::= '"' '"' '"'									=> ''
                       | <anything>:a <stringtripledouble i>:q			=> a+q


# Matches a series of comma-separated values in brackets
tuple :i ::= <token '('> <tupleval i>:t									=> t

tupleval :i ::= <token ')'>												=> ''
              | <thing i>:t <tupleval i>:v								=> t+v


# Matches a series of comma-separated values in square brackets
list :i ::= <token '['> <listval i>:l									=> l

listval :i ::= <token ']'>												=> ''
             | <thing i>:t <listval i>:v								=> t+v


# Matches Python's null object
none :i ::= <token 'None'>												=> 'None'

## The following contain Python's precedence rules
## Backquote
#prec1 :i ::= <backquote i>:b											=> b
## Dictionary definition
#prec2 :i ::= <dict i>:d													=> d
## List definition
#prec3 :i ::= <listnode i>:l												=> l
## Tuple definition and bindings (assign and delete)
#prec4 :i ::= <tuplenode i>:t											=> t
#           | <del i>:d													=> d
#           | <assign i>:a												=> a
#           | <asstuple i>:a												=> a
#           | <assname i>:a												=> a
#           | <assattr i>:a												=> a
## Function calls
#prec5 :i ::= <callfunc i>:c												=> c
## Slices
#prec6 :i ::= <slice i>:s												=> s
#           | <sliceobj i>:s												=> s
## Subscription
#prec7 :i ::= <subscription i>:s											=> s
## Attribute reference
#prec8 :i ::= <getattr i>:g												=> g
## Exponentiation
#prec9 :i ::= <power i>:p												=> p
## Bitwise NOT
#prec10 :i ::= <bitwisenot i>:b											=> b
## Positive and negative
#prec11 :i ::= <unaryadd i>:u											=> u
#            | <unarysub i>:u											=> u
## Multiplication, division and remainder
#prec12 :i ::= <mul i>:m													=> m
#            | <div i>:d													=> d
#            | <mod i>:m													=> m
## Addition and subtraction
#prec13 :i ::= <add i>:a													=> a
#            | <sub i>:s													=> s
## Shifts
#prec14 :i ::= <leftshift i>:l											=> l
#            | <rightshift i>:r											=> r
## Bitwise AND
#prec15 :i ::= <bitwiseand i>:b											=> b
## Bitwise XOR
#prec16 :i ::= <bitwisexor i>:b											=> b
## Bitwise OR
#prec17 :i ::= <bitwiseor i>:b											=> b
## Comparisons
#prec18 :i ::= <compare i>:c												=> c
## Identity tests
##prec19 :i ::= <>:=>
## Membership tests
##prec20 :i ::= <>:=>
## Boolean NOT
#prec21 :i ::= <not i>:n													=> n
## Boolean AND
#prec22 :i ::= <and i>:a													=> a
## Boolean OR
#prec23 :i ::= <or i>:o													=> o
## Lambda
#prec24 :i ::= <lambda i>:l												=> l
"""

g = OMeta.makeGrammar(strip_comments(gram), {'match_args':match_args, 'from_flag':from_flag})

if __name__ == '__main__':
	try:
		mode = "none"
		if sys.argv[2].strip() == "list":
			mode = "list"
		elif sys.argv[2].strip() == "finderror":
			mode = "finderror"
		if not mode is "none":
			ins = open(sys.argv[1], 'r')
			parsefiles = []

			for line in ins.readlines():
				parsefiles.append(line.strip())
			ins.close()

			o1 = open('DONTWORK', 'w')
			o2 = open('DOWORK', 'w')
			o3 = open('REC', 'w')
			o4 = open('SYN', 'w')

			for parse_number, toparse in enumerate(parsefiles):
				print str(len(parsefiles)-parse_number)
				try:
					tree = str(compiler.parseFile(toparse))
				except SyntaxError:
					o4.write(toparse+'\n')
					o4.flush()
					continue
				except IOError:
					o4.write(toparse+'\n')
					o4.flush()
					continue
				ast_tree = g(tree)
				try:
					generated = ast_tree.apply('any')
				except RuntimeError:
					o3.write(toparse+'\n')
					o3.flush()
					continue

				try:
					assert str(compiler.parse(generated)) == tree
					o2.write(toparse+'\n')
					o2.flush()
					if mode == "finderror":
						sys.exit()
				except AssertionError:
					o1.write(toparse+'\n')
					o1.flush()
					if mode == "finderror":
						sys.exit()
				except IndentationError:
					o1.write(toparse+'\n')
					o1.flush()
					if mode == "finderror":
						sys.exit()
				except SyntaxError:
					o1.write(toparse+'\n')
					o1.flush()
					if mode == "finderror":
						sys.exit()
			sys.exit()
	except IndexError:
		try:
			toparse = sys.argv[1]
		except:
			toparse = 'transformer.py'

	try:
		tree = str(compiler.parseFile(toparse))
	except SyntaxError:
		print toparse + ": SyntaxError"
		sys.exit()

	print "Assigning input"

	ast_tree = g(tree)

	print "Applying grammar"

	generated = ast_tree.apply('any')

	try:
		tree2 = str(compiler.parse(generated))
	except SyntaxError:
		print "Generated code does not parse"
	try:
		assert tree2 == tree
		print "Success"
	except:
		print "Fail"
		try:
			t1 = ''
			wrong = False
			for x in range(len(tree)):
				if wrong:
					t1 = t1 + tree[x]
				else:
					if tree[x] == tree2[x]:
						t1 = t1 + tree[x]
					else:
						t1 = t1 + '\n|ERROR|\n'+tree[x]
						wrong = True
			print t1
			print '--------------------------------------------------------'
			wrong = False
			t2 = ''
			for x in range(len(tree)):
				if wrong:
					t2 = t2 + tree2[x]
				else:
					if tree[x] == tree2[x]:
						t2 = t2 + tree2[x]
					else:
						t2 = t2 + '\n|ERROR|\n'+tree2[x]
						wrong = True
			print t2
			print '--------------------------------------------------------'
		except:
			print tree
			print '===================================================='
			try:
				print tree2
				print '--------------------------------------------------------'
			except:
				pass
		print generated
