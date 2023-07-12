from python_actr import *  

# README!!!!
# This is an SGOMS model of a barista making a cappuccino
# The barista makes two cappuccinos: one with cow milk and one with oat milk.
# The oat milk cappuccino results from an alteration request made by the customer.
# The alteration request leads to an intervention by the barista, where it selects oat milk instead of the usual cow milk. 
# The barista makes a cappuccino using the same methods for both milk types.
# The ability to swap milk types results from declarative knowledge of each milk type, along with metadata about those milk types represented by memory typing (slot names and additional slot:value pairs)
# The barista has been provided declarative memory chunks that allow it to differentiate between cappuccinos with each milk type, so long as it can recall which milk type it used
# This provides interventional knowledge that can be further constructed into counterfactual knowledge in later versions. This interventional knowledge is fundamental to causal reasoning.
# For a more technical understanding of how this model works under the hood, please read my comments below. Significant lines have been given comments that describe what the line does for the overall model.
# Many of these lines are contextually reliant on prior lines, so please don't consider each line in a vaccum; read them all at least once in order if you want to get a clear idea of how this works.
# Thank you for reading!


class Cafe_Environment(Model):
    oat_milk = Model(isa='oat_milk')
    cow_milk = Model(isa='cow_milk')
    pass

class MotorModule(Model):
    pass

class Barista(ACTR):
    
    pu_focus=Buffer() # planning unit buffer
    ut_focus=Buffer() # unit task buffer
    method_focus=Buffer() # method buffer
    op_focus=Buffer() # operator buffer

    DMBuffer=Buffer()
    DM=Memory(DMBuffer)
    img=Buffer()
    motor=Buffer()

    method=Buffer()
    

# DECLARATIVE MEMORY

    DM.add('coffee:cappuccino pu:cappuccino')

    # Cafe Planning Unit
    DM.add('ut:cappuccino ut0:espresso ut1:steamedmilk')

    # Cappuccino Unit Tasks

    ## Espresso Unit Task
    DM.add('ut:espresso mtd:portafilter')

    ## Steamed Milk Unit Tasks
    DM.add('ut:steamedmilk mtd:grabmilk')
    DM.add('ut:steamedmilk mtd:grabpitcher')

    #Serve Cappuccino Unit Tasks
    DM.add('ut:servecappuccino ut2:servecappuccino2')
    DM.add('ut:servecappuccino2 pu:defaultmode')

    #Espresso Methods
    DM.add('mtd0:portafilter mtd1:grindbeans')
    DM.add('mtd1:grindbeans mtd2:attachfilter')
    DM.add('mtd2:attachfilter mtd3:grabcup')
    DM.add('mtd3:grabcup mtd4:pressbutton')
    DM.add('mtd4:pressbutton mtd5:pullshot')

    #Steamed Milk Methods
    DM.add('mtd0:grabmilk mtd1:grabpitcher')
    DM.add('mtd0:grabpitcher mtd1:grabmilk')
    DM.add('mtd1:grabpitcher mtd2:pourmilk')
    DM.add('mtd1:grabmilk mtd2:pourmilk')
    DM.add('mtd2:pourmilk mtd3:steammilk')
    DM.add('mtd3:steammilk mtd4:poursteamedmilk')
    DM.add('mtd4:poursteamedmilk mtd5:topwithfoam')
    DM.add('mtd5:topwithfoam ut:servecappuccino')


    # General Milk Knowledge
    DM.add('drink:oat_milk called:oat_milk isa:milk')
    DM.add('drink:cow_milk called:milk isa:milk')
    # UT Milk Knowledge
    DM.add('milk:cow_milk called:milk isa:default')

# CUSTOMER PRODUCTIONS

    def init(): # initializes model and provides task for agent
        print("Can I get a cappuccino?") # The customer requests a cappuccino
        customer_choice = 'cow_milk' # set customer choice to either cow_milk or oat_milk
        method.set(customer_choice)

    def cow_milk(method='cow_milk'): # When the customer makes no alteration request
        drinktype = cow_milk.isa
        drinkname = 'milk'
        milktype = ("drink:"+drinktype+" called:"+drinkname+" isa:milk")
        DM.request(milktype)
        method.set('milkquestion')
        
    def oat_milk(method='oat_milk'): # When the customer makes an alteration request for oat milk
        drinktype = oat_milk.isa
        drinkname = 'oat_milk'
        milktype = ("drink:"+drinktype+" called:"+drinkname+" isa:milk")
        print("Please use "+drinktype) # The customer asks for oat milk
        DM.request(milktype) # The barista recalls the alteration request
        method.set('milkquestion')

# BARISTA PRODUCTIONS
    
    def milk(method='milkquestion', DMBuffer='drink:?drink called:?milk isa:milk'): # Barista either recalls either the milk they must use (from def cow_milk) or the milk the customer requested (from def oat_milk)
        img.chunk = DMBuffer.chunk # The barista stores a memory of that milk for future use
        DM.request('milk:?drink called:?name isa:?utitem') # Having retrieved a specific milk for this task, they recall if this milk is either the default for the cappuccino unit 
        method.set('planselection')

    # CAFE PLANNING UNIT

    # Latte Unit Task
    # Cortado Unit Task
    # Cold Brew Unit Task
    # Cappuccino Unit Task
    def swap(method='planselection', img='drink:?milktype called:?milk isa:milk', DMBuffer=None): # If the milk is an alteration, the barista adapts to that alteration
        print("Okay, I'll use "+milktype) # the barista then confirms the alteration to the customer
        DM.add('milk:?milktype called:?milktype isa:alternative') # the barista adds to declarative memory that it can use oat_milk as a replacement for cow_milk - this is NEW unit task knowledge
        method.set('swap2')

    def swap2(method='swap2', img='drink:?milktype called:?milk isa:milk'): # A separate production is fired due to Python ACT-R constraints - a new 50ms production fires to make a request from DM
        DM.request('milk:?milktype called:?name isa:alternative') # The barista now has an alternative in its unit task declarative memory it can recall AND USE!!
        method.set('planselection')
    
    def taskselection(method='planselection', DMBuffer='milk:?drink called:?name isa:?milkkind'): #regardless of whether it is a default or alteration milk, the barista selects a unit task from the planning unit
        img.chunk = DMBuffer.chunk
        DM.request('coffee:cappuccino pu:cappuccino')
        method.set('cappuccinotime')

    def cappuccino(method='cappuccinotime', DMBuffer='coffee:cappuccino pu:?plan0'):
        print("One cappuccino coming up!")
        DM.request('ut:?plan0 ut0:?task0 ut1:?task1')

    ## Espresso Unit Task
    def espresso(DMBuffer='ut:?plan0 ut0:?task0 ut1:?task1'):
        print("First I need the portafilter.")
        DM.request('ut:?task0 mtd:?method0')
        method.set('espresso0')
        
    ### Espresso Method
    def portafilter(method='espresso0', DMBuffer='ut:espresso mtd:?method0'): #DMBuffer's UT should always match the set of methods about to be used
        print("Grabbing the portafilter")
        motor.set('grab')
        DM.request('mtd0:?method0 mtd1:?method1')
        method.set('espresso1')

    def grindbeans(method='espresso1', DMBuffer='mtd0:portafilter mtd1:?method1'):
        print("Grinding beans in portafilter")
        motor.set('grind')
        DM.request('mtd1:?method1 mtd2:?method2')
        method.set('espresso2')

    def attachfilter(method='espresso2', DMBuffer='mtd1:grindbeans mtd2:?method2'):
        print("Attaching portafilter to grouphead")
        motor.set('lock')
        DM.request('mtd2:?method2 mtd3:?method3')
        method.set('espresso3')

    def grabcup(method='espresso3', DMBuffer='mtd2:attachfilter mtd3:?method3'):
        print("Grabbing a cup")
        motor.set('grab')
        DM.request('mtd3:?method3 mtd4:?method4')
        method.set('espresso4')

    def pressbutton(method='espresso4', DMBuffer='mtd3:grabcup mtd4:?method4'):
        print("Press the espresso button")
        motor.set('press')
        DM.request('mtd4:?method4 mtd5:?method5')
        method.set('espresso5')

    def pullshot(method='espresso5', DMBuffer='mtd4:pressbutton mtd5:?method5'):
        print("Wait while the espresso shot is pulled, pouring into the glass")
        motor.set('wait')
        DM.request('ut:steamedmilk mtd:?method0')
        method.set('steamedmilk0')

    ## Steamed Milk Unit Task ## This is currently passed to from the last method of the Espresso UT sequentially, but later versions could do this situated (Eg. IF Espresso UT is done, THEN Steamed Milk UT)
    def steamedmilk(method='steamedmilk0', DMBuffer='ut:steamedmilk mtd:?method0', img='milk:?drink called:?milk isa:?uttype'): # img is used to recall the milk to be used (from memory of the unit task's default or customer alteration)
        print("Now i have to steam the "+milk)
        DM.request('mtd0:?method0 mtd1:?method1')
        method.set('steamedmilk1')

    ### Steamed Milk Method
    def grabmilk1(method='steamedmilk1', DMBuffer='mtd0:grabmilk mtd1:?method1', img='milk:?drink called:?milk isa:?uttype'):
        print("Grabbing the "+milk)
        motor.set('grab')
        DM.request('mtd1:?method1 mtd2:?method2')
        method.set('steamedmilk2')

    def grabpitcher1(method='steamedmilk2', DMBuffer='mtd1:grabpitcher mtd2:?method2'):
        print("Grabbing a pitcher")
        motor.set('grab')
        DM.request('mtd2:?method2 mtd3:?method3')
        method.set('steamedmilk3')

    def grabpitcher2(method='steamedmilk1', DMBuffer='mtd0:grabpitcher mtd1:?method1'):
        print("Grabbing a pitcher")
        motor.set('grab')
        DM.request('mtd1:?method1 mtd2:?method2')
        method.set('steamedmilk2')

    def grabmilk2(method='steamedmilk2', DMBuffer='mtd1:grabmilk mtd2:?method2', img='milk:?drink called:?milk isa:?uttype'):
        print("Grabbing the "+milk)
        motor.set('grab')
        DM.request('mtd2:?method2 mtd3:?method3')
        method.set('steamedmilk3')

    def pourmilk(method='steamedmilk3', DMBuffer='mtd2:pourmilk mtd3:?method3', img='milk:?drink called:?milk isa:?uttype'):
        print("Pouring the "+milk)
        motor.set('pour')
        DM.request('mtd3:?method3 mtd4:?method4')
        method.set('steamedmilk4')

    def steammilk(method='steamedmilk4', DMBuffer='mtd3:steammilk mtd4:?method4', img='milk:?drink called:?milk isa:?uttype'):
        print("Steaming the "+milk)
        motor.set('steam')
        DM.request('mtd4:?method4 mtd5:?method5')
        method.set('steamedmilk5')

    def poursteamedmilk(method='steamedmilk5', DMBuffer='mtd4:poursteamedmilk mtd5:?method5', img='milk:?drink called:?milk isa:?uttype'):
        print("Pouring the steamed "+milk)
        motor.set('pour')
        DM.request('mtd5:?method5 ut:?task2')
        method.set('steamedmilk6')

    def topwithfoam(method='steamedmilk6', DMBuffer='mtd5:topwithfoam ut:?task2'):
        print("Topping the cappuccino with foam")
        motor.set('scoop')
        DM.request('ut:?task2 ut2:?task3')
        method.set('servecappuccino')

    ## Serve Cappuccino Unit Task
    ### Serve Cappucino Method
    def servecappuccino(method='servecappuccino', DMBuffer='ut:servecappuccino ut2:?task3'):
        motor.set('serve')
        DM.request('ut:servecappuccino2 pu:?pu')
        method.set('servecappuccino2')

    def servecappuccino2(method='servecappuccino2', DMBuffer='ut:servecappuccino2 pu:?pu'):
        print("Here's your cappuccino. Enjoy!") # because I can't put it in the servecappuccino production without "serving" happening after it
        print("------------------------------")
        print("Which Unit Task DM Chunk was used to select a milk?")
        print(img.chunk)
        method.set('rerun')

    # Auto-Rerun Procedure - used to rerun the model after the initial default milk choice to add in the alteration for the 2nd customer, using oat milk
    def rerun(method='rerun',img='milk:cow_milk called:?milk isa:?uttype'):
        print("...............")
        print("NOW WE RUN WITH THE ALTERATION: OAT MILK")
        print("...............")
        method.set('oat_milk')

    # Generalized Motor Productions (Operators)
    
    #### Grind Operator
    def grind(motor='grind'):
        print("Operator: Grinding")
        motor.set('done')

    #### Lock Operator
    def lock(motor='lock'):
        print("Operator: Locking")
        motor.set('done')

    #### Grab Operator
    def grab(motor='grab'):
        print("Operator: Grabbing")
        motor.set('done')

    #### Press Operator
    def press(motor='press'):
        print("Operator: Pressing")
        motor.set('done')

    #### Wait Operator
    def wait(motor='wait'):
        print("Operator: Waiting")
        motor.set('waiting')

    #### Pour Operator
    def pour(motor='pour'):
        print("Operator: Pouring")
        motor.set('done')

    #### Scoop Operator
    def scoop(motor='scoop'):
        print("Operator: Scooping")
        motor.set('done')
        
    #### Steam Operator
    def steam(motor='steam'):
        print("Operator: Steaming")
        motor.set('done')

    #### Serve Operator
    def serve(motor='serve'):
        print("Operator: Serving")
        motor.set('done')


bolas=Barista()
env=Cafe_Environment()
env.agent=bolas

#log_everything(env)
env.run()
