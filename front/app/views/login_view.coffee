{SessionModel} = require 'models/session_model'
{baseContext, serializeForm} = require 'helpers'

class exports.LoginView extends Backbone.View
  className: 'login'
  template: require './templates/login'
  events:
    "submit #signin-form": "submit"
    "click #signin-form [type='submit']": "submit"
    "click button": "submit"

  initialize: ->
    @$el.find("form").submit ->
      return false

  render: ->
    @$el.html @template(baseContext)
    @el

  submit: (ev) ->
    try
      $form = $(ev.target).parents 'form'
      data = serializeForm $form
      session = new SessionModel data
      console.log session.toJSON()
    catch error
      console.log error
    return false
