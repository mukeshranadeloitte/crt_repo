*** Settings ***
Documentation                   OCM Business scenario
Library                         QForce
Library                         String
Library                         QWeb
Library                         BuiltIn
Library                         QVision
Library                         FakerLibrary

*** Test Cases ***
UserCreation
    OpenBrowser        chrome
    GoTo               https://orgfarm-fae880852c-dev-ed.develop.lightning.force.com
