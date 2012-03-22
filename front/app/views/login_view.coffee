{LoginModel} = require 'models/session_model'
{GenericView} = require 'views/generic_view'

{baseContext, serializeForm} = require 'helpers'

class exports.LoginView extends GenericView
  className: 'login'
  template: require './templates/login'
  events:
    "click #signin-form [type='submit']": "submit"

  initialize: ->
    @model = new LoginModel
    @model.on 'error', (model, response) =>
      for field, message of response
        @renderError field, message

    app.homeView.getCurrentUser
      success: (model, resp) =>
        @model.set model.toJSON(), silent: true

  render: ->
    @$el.html @template(baseContext)
    @el

  submit: (ev) ->
    @clearErrors()
    data = serializeForm($(ev.target).parents 'form')
    @model.save data,
      success: -> console.log 'success'
      error: () =>
        console.log 'error'
    return false

