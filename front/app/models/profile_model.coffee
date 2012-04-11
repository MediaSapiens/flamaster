class exports.ProfileModel extends Backbone.Model
  urlRoot: '/account/profiles/'

  events:
    'change:id': "updateLinks"

  updateLinks: (model, attr) ->
    @front =
      edit: "/#!/profiles/#{attr}/edit"
      show: "/#!/profiles/#{attr}"

  initialize: ->
    for event, func of @events
      @on event, @[func]

  getUsername: ->
    [first, last] = [@get('first_name'), @get('last_name')]
    username = $.trim "#{first? and first or ''} #{last? and last or ''}"
    username.length and username or "please, fill your profile data"
