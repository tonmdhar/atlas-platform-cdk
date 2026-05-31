package com.atlas.platform.service;

import com.atlas.platform.model.Item;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import software.amazon.awssdk.enhanced.dynamodb.DynamoDbEnhancedClient;
import software.amazon.awssdk.enhanced.dynamodb.DynamoDbTable;
import software.amazon.awssdk.enhanced.dynamodb.Key;
import software.amazon.awssdk.enhanced.dynamodb.TableSchema;
import software.amazon.awssdk.enhanced.dynamodb.model.ScanEnhancedRequest;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Service
@RequiredArgsConstructor
@Slf4j
public class ItemService {

    private final DynamoDbEnhancedClient enhancedClient;

    @Value("${dynamodb.table.name}")
    private String tableName;

    private DynamoDbTable<Item> getTable() {
        return enhancedClient.table(tableName, TableSchema.fromBean(Item.class));
    }

    public Item createItem(Item item) {
        if (item.getId() == null || item.getId().isEmpty()) {
            item.setId(UUID.randomUUID().toString());
        }
        String now = Instant.now().toString();
        item.setCreatedAt(now);
        item.setUpdatedAt(now);

        getTable().putItem(item);
        log.info("Created item with id: {}", item.getId());
        return item;
    }

    public Optional<Item> getItem(String id) {
        Key key = Key.builder()
                .partitionValue(id)
                .build();

        Item item = getTable().getItem(key);
        log.info("Retrieved item with id: {}", id);
        return Optional.ofNullable(item);
    }

    public List<Item> getAllItems() {
        List<Item> items = new ArrayList<>();
        getTable().scan(ScanEnhancedRequest.builder().build())
                .items()
                .forEach(items::add);
        log.info("Retrieved {} items", items.size());
        return items;
    }

    public Optional<Item> updateItem(String id, Item updatedItem) {
        Optional<Item> existingItem = getItem(id);

        if (existingItem.isEmpty()) {
            log.warn("Item not found with id: {}", id);
            return Optional.empty();
        }

        Item item = existingItem.get();
        if (updatedItem.getName() != null) {
            item.setName(updatedItem.getName());
        }
        if (updatedItem.getDescription() != null) {
            item.setDescription(updatedItem.getDescription());
        }
        item.setUpdatedAt(Instant.now().toString());

        getTable().putItem(item);
        log.info("Updated item with id: {}", id);
        return Optional.of(item);
    }

    public boolean deleteItem(String id) {
        Key key = Key.builder()
                .partitionValue(id)
                .build();

        Item deletedItem = getTable().deleteItem(key);
        boolean deleted = deletedItem != null;
        log.info("Deleted item with id: {}, success: {}", id, deleted);
        return deleted;
    }
}
