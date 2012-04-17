{GenericView} = require 'views/generic_view'
{NavView} = require 'views/nav_view'

class exports.HomeView extends GenericView
  id: 'home-view'
  template: require('./templates/home')

  initialize: ->
    @navView = new NavView
      model:
        index: ["Index", '!/']
        signup: ["Sign Up", '!/signup']
        login: ["Login", '!/login']
      session: @getCurrentUser()


  render: ->
    @$el.html @template
    @$el.find("#nav-container").html @navView.render()
    @el

