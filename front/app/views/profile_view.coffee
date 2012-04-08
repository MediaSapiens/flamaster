{ProfileModel} = require 'models/profile_model'

{GenericView} = require 'views/generic_view'

{baseContext, serializeForm} = require 'helpers'

class exports.ProfileView extends GenericView
  className: 'profile'
  template: require './templates/profile'

  events:
    "click a#edit-profile": "edit"

  actions: ->
    show: =>

  edit: (ev) ->
    false

  initialize: (options) ->
    console.log 'routes', options.routes
    # @model = new ProfileModel id: options.id

  render: ->
    baseContext = _.extend baseContext,
      profile: @model
    @$el.html @template(baseContext)
    @el

  push: (options) ->
    console.log 'pushed': options

    if typeof(options.id) isnt 'undefined'
      @model = new ProfileModel id: options.id
      @model.fetch
        success: => @trigger options.action
