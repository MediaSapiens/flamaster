{BrunchApplication} = require 'helpers'

{MainRouter} = require 'routers/main_router'
{ProfileRouter} = require 'routers/profile_router'

{HomeView} = require 'views/home_view'

class exports.Application extends BrunchApplication
  # This callback would be executed on document ready event.
  # If you have a big application, perhaps it's a good idea to
  # group things by their type e.g. `@views = {}; @views.home = new HomeView`.
  initialize: ->
    # router section
    @router = new MainRouter
    @profileRouter = new ProfileRouter

  render: (ViewClass, options=undefined) ->
    @layout()
    if typeof(ViewClass) is 'function'
      classView = options? and new ViewClass(options) or new ViewClass
      @inject classView.render()
      classView

  inject: (html) ->
    @layout()
    @$container.html html

  layout: ->
    if @homeView is undefined
      @homeView = new HomeView
      $('body').html @homeView.render()
      @$container = $ '#content'

window.app = new exports.Application
window.mediator = _({}).extend(Backbone.Events)
