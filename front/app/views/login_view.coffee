{SessionModel} = require 'models/session_model'

class exports.LoginView extends Backbone.View
  className: 'login'
  template: require './templates/login'

  render: ->
    @$el.html @template()
    @el
