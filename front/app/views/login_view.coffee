{SessionModel} = require 'models/session_model'
{baseContext, serializeForm} = require 'helpers'

class exports.LoginView extends Backbone.View
  className: 'login'
  template: require './templates/login'
  events:
    "submit #signin-form": "submit"

  render: ->
    @$el.html @template(baseContext)
    @el

  submit: (ev) ->
    data = serializeForm $(ev.target)
    console.log data
    false
