    def mousedown(self, gesture, data, x, y):
        pos = Vec2(x, y).to_world(self.transform)

        self.mouse_start = Vec2(x, y)

        match (gesture.get_current_button()):
            case 1:
                self.left_down = True
                state = self.get_state(pos)
                arrow = self.get_arrow(pos)

                if self.shift:
                    pos = Vec2(x, y).to_world(self.transform)
                    if state != None:
                        self.preview_arrow = PreviewArrow()
                        self.preview_arrow.start = state
                        self.preview_arrow.end = pos
                        self.preview_start = Vec2(x, y)

                elif state != None and not self.shift and not self.control:
                    self.select(state)
                elif arrow != None and not self.shift and not self.control:
                    self.select(arrow)
                elif not self.control and not self.shift:
                    state = State()
                    state.position = Vec2(x, y).to_world(self.transform)
                    state.label = "q"+str(len(self.states))

                    self.active_element = state
                    self.states.append(state)

            case 2:
                self.middle_down = True
                state = self.get_state(pos)
                if state == None:
                    return
                if self.shift:
                    state.initial = not state.initial
                else:
                    state.final = not state.final

            case 3:
                state = self.get_state(pos)
                if state:
                    for arrow in self.arrows:
                        if arrow.start == state or arrow.end == state:
                            self.arrows.remove(arrow)
                    self.states.remove(state)
                arrow = self.get_arrow(pos)
                if arrow:
                    self.arrows.remove(arrow)
                self.right_down = True

        self.canvas.queue_draw()

    def mousemove(self, motion, x, y):
        pos = Vec2(x, y).to_world(self.transform)

        if self.middle_down:
            self.transform.offset.x += (x - self.mouse_start.x) / self.transform.scale
            self.transform.offset.y += (y - self.mouse_start.y) / self.transform.scale
        if self.shift and self.preview_arrow != None:
            self.preview_arrow.end = self.preview_start.plus(Vec2(x, y)).to_world(self.transform)
        if self.selected and self.active_element.type == "state":
            self.active_element.position = self.preview_start.plus(Vec2(x, y)).to_world(self.transform)
        self.mouse_start = Vec2(x, y)

        arrow = self.get_arrow(pos)
        state = self.get_state(pos)

        self.hovered_element = arrow if arrow != None else state if state != None else None
        self.moved = True


        self.canvas.queue_draw()


    def mouseup(self, gesture, data, x, y):
        pos = Vec2(x, y).to_world(self.transform)

        if self.left_down and not self.moved:
            self.fixed.set_visible(True)
            if self.active_element.type == "state":
                self.state_menu.show(self, self.active_element, self.preview_start.x, self.preview_start.y)
            if self.active_element.type == "arrow":
                self.arrow_menu.show(self, self.active_element, self.preview_start.x, self.preview_start.y)

        if self.preview_arrow != None:
            state = self.get_state(self.preview_arrow.end)
            if state != None:
                arrow = Arrow()
                arrow.start = self.preview_arrow.start
                arrow.end = state
                self.arrows.append(arrow)
                self.active_element = arrow
                self.fixed.set_visible(True)
                self.arrow_menu.show(self, self.active_element, self.preview_start.x, self.preview_start.y)


        self.preview_arrow = None
        self.preview_start = None

        self.left_down = False
        self.middle_down = False
        self.right_down = False

        self.selected = False
        self.active_element = None

        self.canvas.queue_draw()

    def select(self, w):
        self.active_element = w
        self.selected = True

    def get_state(self, pos):
        for state in self.states:
            rad = state.position.minus(pos).length()
            if rad < self.radius:
                return state
        return None
    def get_arrow(self, pos):
        lib_draw.update_arrows(self)
        for arrow in self.arrows:
            arr = arrow.start.position.plus(arrow.end.position).times(0.5)
            if arrow.offset != 0 and arrow.start != arrow.end:
                arr = arr.plus(Vec2(0, math.sqrt(arrow.offset*arrow.offset)*5).rotated(arrow.end.position.minus(arrow.start.position).angle()))
            if arrow.start == arrow.end:
                arr = arrow.start.position.plus(self.self_arrow_offset).minus(Vec2(0, self.radius+5))
            rad = arr.minus(pos).length()
            if rad < self.arrow_radius:
                return arrow
        return None

