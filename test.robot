*** Settings ***
Documentation                   OCM Business scenario
Library                         QForce
Library                         String
Library                         QWeb
Library                         BuiltIn
Library                         QVision
Library                         FakerLibrary
Resource                        common.robot
Suite Setup                     Setup Browser
 
*** Test Cases ***
UserCreation
    Open Browser    about:blank    chrome
    GoTo            https://orgfarm-fae880852c-dev-ed.develop.lightning.force.com
    TypeText                    Username                    mukeshrana1909.8b565d512db3@agentforce.com             delay=1
    TypeSecret                  Password                    Salesforce@032026
    ClickText                   Log In

    LaunchApp    Contacts
    ClickText    New                        partial_match=False
    UseModal    On
    PickList    Salutation    Mr.
    TypeText    First Name    Test 1
    TypeText    Last Name    User
    ClickText    Save    partial_match=False
    UseModal    Off
