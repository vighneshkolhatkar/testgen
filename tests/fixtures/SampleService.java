package com.example.service;

import com.example.model.User;
import com.example.repository.UserRepository;
import com.example.exception.UserNotFoundException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service
public class UserService {

    private final UserRepository userRepository;

    @Autowired
    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    public User createUser(String name, String email) {
        User user = new User(name, email);
        return userRepository.save(user);
    }

    public User getUserById(Long id) throws UserNotFoundException {
        return userRepository.findById(id)
            .orElseThrow(() -> new UserNotFoundException("User not found: " + id));
    }

    public List<User> getAllUsers() {
        return userRepository.findAll();
    }

    public User updateEmail(Long id, String newEmail) throws UserNotFoundException {
        User user = getUserById(id);
        user.setEmail(newEmail);
        return userRepository.save(user);
    }
}
