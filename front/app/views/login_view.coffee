{SessionModel} = require 'models/session_model'
{GenericView} = require 'views/generic_view'

{baseContext, serializeForm} = require 'helpers'

class exports.LoginView extends GenericView
  className: 'login'
  template: require './templates/login'
  events:
    "click #signin-form [type='submit']": "submit"

  initialize: ->
    console.log 'initialized'
    @$el.find("form").submit ->
      return false

  render: ->
    #console.log 'test'
    @$el.html @template(baseContext)
    @el

  submit: (ev) ->
    $form = $(ev.target).parents 'form'
    @clearErrors()
    session = new SessionModel(serializeForm $form)
    session.on 'error', (session, error) =>
      for field, message of error
        @renderError field, message
    session.save
      success: ->
        console.log 'success', arguments
      error: ->
        console.log 'error', arguments
    return false

